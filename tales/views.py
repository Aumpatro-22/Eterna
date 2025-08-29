from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Max
from django.urls import reverse
from .models import Tale, Chapter
from .forms import TaleForm, ChapterForm
from django.contrib import messages  # NEW
from django.http import Http404  # NEW

def tale_list(request):
    q = (request.GET.get('q') or '').strip()
    qs = Tale.objects.all()
    if not request.user.is_authenticated:
        qs = qs.filter(is_public=True)
    if q:
        qs = qs.filter(title__icontains=q)
    return render(request, 'tales/tale_list.html', {'tales': qs.order_by('-created_at')})

def tale_detail(request, slug):
    # Try case-insensitive slug match first
    tale = Tale.objects.filter(slug__iexact=slug).first()
    if not tale:
        # Fallback: try to resolve from title guess (hyphens to spaces) exactly
        title_guess = slug.replace('-', ' ')
        guess = Tale.objects.filter(title__iexact=title_guess).first()
        if guess:
            return redirect('tales:detail', slug=guess.slug)
        # Fallback: if exactly one icontains match, redirect to it
        candidates = Tale.objects.filter(title__icontains=title_guess)[:2]
        if candidates.count() == 1:
            return redirect('tales:detail', slug=candidates[0].slug)
        # Nothing reasonable found
        raise Http404("Tale not found.")

    if not tale.is_public and (not request.user.is_authenticated or tale.author != request.user):
        return HttpResponseForbidden("This tale is private.")
    # Include drafts for the author
    if request.user.is_authenticated and request.user == tale.author:
        chapters = list(tale.chapters.all())
    else:
        chapters = list(tale.chapters.filter(published=True))
    current = request.GET.get('c')
    current_chapter = chapters[0] if chapters else None
    if current:
        current_chapter = next((ch for ch in chapters if str(ch.order) == str(current)), current_chapter)
    # prev/next
    prev_order = next_order = None
    if current_chapter:
        idx = chapters.index(current_chapter)
        prev_order = chapters[idx-1].order if idx > 0 else None
        next_order = chapters[idx+1].order if idx < len(chapters)-1 else None
    return render(request, 'tales/tale_detail.html', {
        'tale': tale, 'chapters': chapters, 'chapter': current_chapter,
        'prev_order': prev_order, 'next_order': next_order
    })

@login_required
def tale_create(request):
    if request.method == 'POST':
        form = TaleForm(request.POST)
        if form.is_valid():
            tale = form.save(commit=False)
            tale.author = request.user
            tale.save()
            # Redirect straight to add the first chapter
            return redirect('tales:chapter_create', slug=tale.slug)
    else:
        form = TaleForm()
    return render(request, 'tales/tale_create.html', {'form': form})

@login_required
def chapter_create(request, slug):
    tale = get_object_or_404(Tale, slug=slug)
    if tale.author != request.user:
        return HttpResponseForbidden("Only the author can add chapters.")
    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            ch = form.save(commit=False)
            ch.tale = tale
            # Ensure unique order; if taken, append to end
            if Chapter.objects.filter(tale=tale, order=ch.order).exists():
                max_order = tale.chapters.aggregate(Max('order'))['order__max'] or 0
                ch.order = max_order + 1
            ch.save()
            # Redirect to the tale with the new chapter selected (works for drafts too)
            detail_url = reverse('tales:detail', kwargs={'slug': tale.slug})
            return redirect(f"{detail_url}?c={ch.order}")
    else:
        next_order = (tale.chapters.aggregate(Max('order'))['order__max'] or 0) + 1
        form = ChapterForm(initial={'order': next_order})
    return render(request, 'tales/chapter_form.html', {'form': form, 'tale': tale})

@login_required
def chapter_publish(request, slug, chapter_id):
    tale = get_object_or_404(Tale, slug=slug)
    if request.user != tale.author:
        return HttpResponseForbidden("Only the author can publish.")
    ch = get_object_or_404(Chapter, pk=chapter_id, tale=tale)
    if request.method == 'POST' and not ch.published:
        ch.published = True
        ch.save(update_fields=['published'])
    detail_url = reverse('tales:detail', kwargs={'slug': tale.slug})
    return redirect(f"{detail_url}?c={ch.order}")

# NEW: delete a tale (author only)
@login_required
def tale_delete(request, slug):
    tale = get_object_or_404(Tale, slug=slug)
    if request.user != tale.author:
        return HttpResponseForbidden("Only the author can delete this tale.")
    if request.method != 'POST':
        # Only allow POST to delete
        return redirect('tales:detail', slug=tale.slug)
    title = tale.title
    tale.delete()  # cascades to chapters
    messages.success(request, f"Tale '{title}' was deleted.")
    return redirect('tales:list')
