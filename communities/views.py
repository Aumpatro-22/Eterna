from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q
from urllib.parse import unquote  # CHANGED

from .models import Community, Channel, Membership, CommunityMessage
from .forms import CommunityForm, ChannelForm, CommunityMessageForm

def community_list(request):
    q = request.GET.get('q', '').strip()
    qs = Community.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if not request.user.is_authenticated:
        qs = qs.filter(is_public=True)
    context = {'communities': qs.order_by('-created_at')}
    return render(request, 'communities/community_list.html', context)

@login_required
def community_create(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST)
        if form.is_valid():
            community = form.save(commit=False)
            community.owner = request.user
            community.save()
            Membership.objects.create(community=community, user=request.user, role='owner')
            Channel.objects.create(community=community, name='general', is_public=True)
            return redirect('communities:detail', slug=community.slug)
    else:
        initial = {}
        name = request.GET.get('name') or ''
        desc = request.GET.get('desc') or ''
        if name: initial['name'] = unquote(name)[:80]  # CHANGED
        if desc: initial['description'] = unquote(desc)  # CHANGED
        form = CommunityForm(initial=initial)
    return render(request, 'communities/community_create.html', {'form': form})

def community_detail(request, slug, channel_slug=None):
    community = get_object_or_404(Community, slug=slug)
    channels = community.channels.order_by('name')
    channel = channels.first() if channel_slug is None else get_object_or_404(Channel, community=community, slug=channel_slug)
    is_member = request.user.is_authenticated and Membership.objects.filter(community=community, user=request.user).exists()
    can_view = community.is_public or is_member
    if not can_view:
        return HttpResponseForbidden("This community is private.")
    messages_qs = channel.messages.select_related('author')[:50]
    form = CommunityMessageForm()
    return render(request, 'communities/community_detail.html', {
        'community': community,
        'channels': channels,
        'channel': channel,
        'messages': messages_qs[::-1],  # oldest at top
        'is_member': is_member,
        'form': form
    })

@login_required
def join_community(request, slug):
    community = get_object_or_404(Community, slug=slug)
    Membership.objects.get_or_create(community=community, user=request.user, defaults={'role': 'member'})
    return redirect('communities:detail', slug=slug)

@login_required
def leave_community(request, slug):
    community = get_object_or_404(Community, slug=slug)
    Membership.objects.filter(community=community, user=request.user).exclude(role='owner').delete()
    return redirect('communities:list')

@login_required
def post_message(request, slug, channel_slug):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'error': 'Invalid method'}, status=405)
    community = get_object_or_404(Community, slug=slug)
    channel = get_object_or_404(Channel, community=community, slug=channel_slug)
    if not Membership.objects.filter(community=community, user=request.user).exists():
        return JsonResponse({'status': 'error', 'error': 'Not a member'}, status=403)
    form = CommunityMessageForm(request.POST)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.channel = channel
        msg.author = request.user
        msg.save()
        return JsonResponse({
            'status': 'success',
            'author': request.user.username,
            'content': msg.content,
            'created_at': timezone.localtime(msg.created_at).strftime('%b %d, %Y %I:%M %p')
        })
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

def messages_feed(request, slug, channel_slug):
    # Simple polling feed
    community = get_object_or_404(Community, slug=slug)
    channel = get_object_or_404(Channel, community=community, slug=channel_slug)
    since = request.GET.get('since')  # ISO string
    qs = channel.messages.select_related('author').order_by('created_at')
    if since:
        try:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(since)
            if dt:
                qs = qs.filter(created_at__gt=dt)
        except Exception:
            pass
    data = [{
        'author': m.author.username,
        'content': m.content,
        'created_at': timezone.localtime(m.created_at).isoformat()
    } for m in qs[:50]]
    return JsonResponse({'results': data})
