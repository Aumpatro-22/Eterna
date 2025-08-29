from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.http import JsonResponse, HttpResponseForbidden  # CHANGED
from django.db.models import Q, Count  # CHANGED
from django.contrib.auth.models import User  # NEW
from django.urls import reverse  # NEW
from django.contrib.contenttypes.models import ContentType  # NEW
from django.utils import timezone  # NEW
from django.utils.dateparse import parse_datetime  # NEW

from .models import Profile  # NEW
from .models import Reaction, DirectMessage  # NEW
from memorials.models import Memorial  # NEW
from tales.models import Tale  # NEW

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to Eternal Memories.")
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def search_profiles(request):
    q = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))
    # from .models import Profile  # now imported at top

    qs = Profile.objects.select_related('user').filter(public_search=True)
    if q:
        qs = qs.filter(
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(display_name__icontains=q) |
            Q(bio__icontains=q) |
            Q(tags__icontains=q)
        )
    qs = qs.order_by('user__username')[:max(1, min(limit, 20))]

    def avatar_url(p):
        return p.profile_image.url if p.profile_image else ''

    data = [
        {
            'id': p.user.id,
            'username': p.user.username,
            'display_name': p.display_name or f"{p.user.first_name} {p.user.last_name}".strip(),
            'bio': (p.bio or '')[:120],
            'tags': p.tags_list(),
            'avatar': avatar_url(p),
            # CHANGED: deep link to profile explore
            'url': request.build_absolute_uri(reverse('profile', kwargs={'username': p.user.username}))
        }
        for p in qs
    ]
    return JsonResponse({'results': data})

# NEW: profile explore page
def profile_detail(request, username):
    profile_user = User.objects.filter(username=username).first()
    if not profile_user:
        return render(request, 'users/profile_detail.html', {'not_found': True}, status=404)

    # Lists
    memorials = Memorial.objects.filter(creator=profile_user).select_related('creator')
    tales = Tale.objects.filter(author=profile_user)

    # Reaction counts for memorials
    ct_mem = ContentType.objects.get_for_model(Memorial)
    mem_ids = list(memorials.values_list('id', flat=True))
    mem_reacts = (Reaction.objects.filter(content_type=ct_mem, object_id__in=mem_ids)
                  .values('object_id', 'reaction_type').annotate(c=Count('id')))
    mem_counts = {mid: {'like': 0, 'love': 0, 'support': 0} for mid in mem_ids}
    for r in mem_reacts:
        mem_counts[r['object_id']][r['reaction_type']] = r['c']

    user_mem_react = {}
    if request.user.is_authenticated and mem_ids:
        user_rs = Reaction.objects.filter(user=request.user, content_type=ct_mem, object_id__in=mem_ids)
        user_mem_react = {r.object_id: r.reaction_type for r in user_rs}

    # Reaction counts for tales
    ct_tale = ContentType.objects.get_for_model(Tale)
    tale_ids = list(tales.values_list('id', flat=True))
    tale_reacts = (Reaction.objects.filter(content_type=ct_tale, object_id__in=tale_ids)
                   .values('object_id', 'reaction_type').annotate(c=Count('id')))
    tale_counts = {tid: {'like': 0, 'love': 0, 'support': 0} for tid in tale_ids}
    for r in tale_reacts:
        tale_counts[r['object_id']][r['reaction_type']] = r['c']

    user_tale_react = {}
    if request.user.is_authenticated and tale_ids:
        user_rs = Reaction.objects.filter(user=request.user, content_type=ct_tale, object_id__in=tale_ids)
        user_tale_react = {r.object_id: r.reaction_type for r in user_rs}

    # Recent DMs (if logged in)
    convo = []
    if request.user.is_authenticated and request.user != profile_user:
        convo = DirectMessage.objects.filter(
            Q(sender=request.user, receiver=profile_user) | Q(sender=profile_user, receiver=request.user)
        ).order_by('-created_at')[:20]
        convo = list(convo)[::-1]  # oldest first

    # Attach counts and current user reaction to each memorial
    for m in memorials:
        c = mem_counts.get(m.id, {'like': 0, 'love': 0, 'support': 0})
        m.count_like = c.get('like', 0)
        m.count_love = c.get('love', 0)
        m.count_support = c.get('support', 0)
        m.my_react = user_mem_react.get(m.id)

    # Attach counts and current user reaction to each tale
    for t in tales:
        c = tale_counts.get(t.id, {'like': 0, 'love': 0, 'support': 0})
        t.count_like = c.get('like', 0)
        t.count_love = c.get('love', 0)
        t.count_support = c.get('support', 0)
        t.my_react = user_tale_react.get(t.id)

    ctx = {
        'profile_user': profile_user,
        'memorials': memorials,
        'tales': tales,
        'mem_counts': mem_counts,
        'user_mem_react': user_mem_react,
        'tale_counts': tale_counts,
        'user_tale_react': user_tale_react,
        'convo': convo,
    }
    return render(request, 'users/profile_detail.html', ctx)

# NEW: react toggle endpoint
def react(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'Invalid method'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'error': 'Auth required'}, status=401)

    target_type = (request.POST.get('model') or '').strip()
    target_id = request.POST.get('id')
    rtype = (request.POST.get('reaction') or '').strip()
    if rtype not in ('like', 'love', 'support'):
        return JsonResponse({'status': 'error', 'error': 'Invalid reaction'}, status=400)
    try:
        obj_id = int(target_id)
    except (TypeError, ValueError):
        obj_id = None
    if target_type not in ('memorial', 'tale') or not obj_id:
        return JsonResponse({'status': 'error', 'error': 'Bad target'}, status=400)

    model_cls = Memorial if target_type == 'memorial' else Tale
    ct = ContentType.objects.get_for_model(model_cls)
    # Ensure object exists
    if not model_cls.objects.filter(id=obj_id).exists():
        return JsonResponse({'status': 'error', 'error': 'Not found'}, status=404)

    # Toggle logic: single reaction per object per user
    existing = Reaction.objects.filter(user=request.user, content_type=ct, object_id=obj_id).first()
    active = False
    if existing and existing.reaction_type == rtype:
        existing.delete()
        active = False
    else:
        if existing:
            existing.reaction_type = rtype
            existing.save(update_fields=['reaction_type'])
        else:
            Reaction.objects.create(user=request.user, content_type=ct, object_id=obj_id, reaction_type=rtype)
        active = True

    # Recompute counts
    counts_qs = Reaction.objects.filter(content_type=ct, object_id=obj_id) \
        .values('reaction_type').annotate(c=Count('id'))
    counts = {'like': 0, 'love': 0, 'support': 0}
    for r in counts_qs:
        counts[r['reaction_type']] = r['c']

    return JsonResponse({'status': 'ok', 'counts': counts, 'active': active, 'type': rtype})

# NEW: send direct message
def send_dm(request, username):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'Invalid method'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'error': 'Auth required'}, status=401)

    receiver = User.objects.filter(username=username).first()
    if not receiver:
        return JsonResponse({'status': 'error', 'error': 'User not found'}, status=404)
    if receiver == request.user:
        return JsonResponse({'status': 'error', 'error': "Can't message yourself"}, status=400)

    content = (request.POST.get('message') or '').strip()
    if not content:
        return JsonResponse({'status': 'error', 'error': 'Empty message'}, status=400)

    dm = DirectMessage.objects.create(sender=request.user, receiver=receiver, content=content)
    return JsonResponse({
        'status': 'ok',
        'id': dm.id,  # NEW
        'message': dm.content,
        'sender': request.user.username,
        'created_at': dm.created_at.strftime('%b %d, %Y %I:%M %p'),
        'created_at_iso': timezone.localtime(dm.created_at).isoformat()  # NEW
    })

# NEW: full-screen personal chat thread
def dm_thread(request, username):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Auth required")
    other = User.objects.filter(username=username).first()
    if not other:
        return render(request, 'users/dm_thread.html', {'not_found': True}, status=404)
    if other == request.user:
        return HttpResponseForbidden("Cannot chat with yourself")

    # Fetch last 50 messages between users, oldest first for display
    qs = DirectMessage.objects.filter(
        Q(sender=request.user, receiver=other) | Q(sender=other, receiver=request.user)
    ).order_by('-created_at')[:50]
    messages_qs = list(qs)[::-1]

    # Mark received messages as read
    DirectMessage.objects.filter(receiver=request.user, sender=other, is_read=False).update(is_read=True)

    # NEW: latest timestamp of already-rendered messages (list is oldest->newest)
    last_ts = None
    if messages_qs:
        last_ts = timezone.localtime(messages_qs[-1].created_at).isoformat()

    ctx = {
        'other': other,
        'messages': messages_qs,
        # NEW
        'last_ts': last_ts,
    }
    return render(request, 'users/dm_thread.html', ctx)

# NEW: JSON feed for new messages since timestamp (ISO)
def dm_feed(request, username):
    if not request.user.is_authenticated:
        return JsonResponse({'results': []}, status=401)
    other = User.objects.filter(username=username).first()
    if not other:
        return JsonResponse({'results': []}, status=404)

    since = request.GET.get('since')
    qs = DirectMessage.objects.filter(
        Q(sender=request.user, receiver=other) | Q(sender=other, receiver=request.user)
    ).order_by('created_at')
    if since:
        dt = parse_datetime(since)
        if dt:
            qs = qs.filter(created_at__gt=dt)

    data = [{
        'id': m.id,
        'sender': m.sender.username,
        'content': m.content,
        'created_at': timezone.localtime(m.created_at).isoformat()
    } for m in qs[:100]]

    # Mark received messages as read
    DirectMessage.objects.filter(receiver=request.user, sender=other, is_read=False).update(is_read=True)

    # CHANGED: disable caching
    resp = JsonResponse({'results': data})
    resp['Cache-Control'] = 'no-store'
    return resp
