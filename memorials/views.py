import os
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django import forms
from django.core.mail import send_mail, BadHeaderError
import logging

from .models import Memorial, Message, Candle
from .forms import MemorialForm, MessageForm, CandleForm
from .services import GroqService, AIHordeService

logger = logging.getLogger(__name__)

# Helper: download and save a remote image with validation and timeout
def _save_image_from_url(memorial, url, filename_prefix='ai_memorial'):
    try:
        resp = requests.get(url, timeout=20, stream=True)
        resp.raise_for_status()
        ctype = resp.headers.get('Content-Type', '')
        if 'image' not in ctype:
            return False, f"Non-image content received ({ctype or 'unknown type'})"
        ext = 'png'
        if 'jpeg' in ctype or 'jpg' in ctype:
            ext = 'jpg'
        elif 'webp' in ctype:
            ext = 'webp'
        image_name = f"{filename_prefix}_{memorial.name.replace(' ', '_')}.{ext}"
        memorial.image.save(image_name, ContentFile(resp.content), save=False)
        memorial.is_ai_generated_image = True
        return True, None
    except Exception as e:
        logger.exception("Failed to download AI image from %s: %s", url, e)
        return False, str(e)

class HomePageView(ListView):
    model = Memorial
    template_name = 'home.html'
    context_object_name = 'memorials'
    ordering = ['-created_at']
    paginate_by = 6

    def get_queryset(self):
        qs = super().get_queryset().select_related('creator')
        search = (self.request.GET.get('search') or '').strip()
        creator_id = (self.request.GET.get('creator') or '').strip()
        if creator_id.isdigit():
            qs = qs.filter(creator__id=int(creator_id))
        if search:
            qs = qs.filter(
                Q(public_id__iexact=search) |
                Q(name__icontains=search) |
                Q(biography__icontains=search) |
                Q(tribute__icontains=search) |
                Q(creator__username__icontains=search) |
                Q(creator__first_name__icontains=search) |
                Q(creator__last_name__icontains=search)
            )
        return qs

class MemorialDetailView(DetailView):
    model = Memorial
    template_name = 'memorial_detail.html'
    context_object_name = 'memorial'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_form'] = MessageForm()
        context['candle_form'] = CandleForm()
        context['messages'] = self.object.messages.order_by('-created_at')
        context['candles'] = self.object.candles.order_by('-lit_at')
        return context

class MemorialByIdView(DetailView):
    model = Memorial
    template_name = 'memorial_detail.html'
    context_object_name = 'memorial'

    def get_object(self, queryset=None):
        pid = self.kwargs['public_id']
        return Memorial.objects.select_related('creator').get(public_id=pid)

@login_required
def create_memorial(request):
    if request.method == 'POST':
        form = MemorialForm(request.POST, request.FILES)
        if form.is_valid():
            memorial = form.save(commit=False)
            memorial.creator = request.user

            # Ensure robust AI image generation with validation, timeouts, and logging
            if form.cleaned_data.get('use_ai_image'):
                prompt = (form.cleaned_data.get('image_prompt') or '').strip()
                if not prompt:
                    messages.warning(request, "Please provide an image description for AI generation, or upload a photo.")
                elif not getattr(settings, 'AI_HORDE_API_KEY', ''):
                    messages.error(request, "AI image service is not configured. Please try uploading an image instead.")
                else:
                    try:
                        image_payload = AIHordeService.generate_memorial_image(prompt)
                    except Exception as e:
                        logger.exception("AI image generation failed: %s", e)
                        image_payload = None
                        messages.error(request, "AI image generation failed. Please try again later.")
                    if image_payload:
                        if isinstance(image_payload, (bytes, bytearray)):
                            image_name = f"ai_memorial_{memorial.name.replace(' ', '_')}.png"
                            memorial.image.save(image_name, ContentFile(image_payload), save=False)
                            memorial.is_ai_generated_image = True
                        elif isinstance(image_payload, str) and image_payload.startswith('http'):
                            ok, err = _save_image_from_url(memorial, image_payload)
                            if not ok:
                                messages.error(request, f"Could not download generated image. {err}")
                        else:
                            messages.error(request, "AI service response was not a valid image.")
                    else:
                        messages.error(request, "AI image service did not return an image.")

            # Handle AI tribute generation if requested
            if form.cleaned_data['generate_tribute'] and form.cleaned_data['memories']:
                tribute = GroqService.generate_tribute(
                    form.cleaned_data['name'],
                    form.cleaned_data['relationship'],
                    form.cleaned_data['memories']
                )
                memorial.tribute = tribute
            
            memorial.save()
            return redirect('memorial_detail', pk=memorial.pk)
    else:
        form = MemorialForm()
    
    return render(request, 'create_memorial.html', {'form': form})

@login_required
def update_memorial(request, pk):
    memorial = get_object_or_404(Memorial, pk=pk, creator=request.user)
    if request.method == 'POST':
        form = MemorialForm(request.POST, request.FILES, instance=memorial)
        if form.is_valid():
            form.save()
            return redirect('memorial_detail', pk=memorial.pk)
    else:
        form = MemorialForm(instance=memorial)
    
    return render(request, 'update_memorial.html', {'form': form, 'memorial': memorial})

@login_required
def delete_memorial(request, pk):
    memorial = get_object_or_404(Memorial, pk=pk, creator=request.user)
    if request.method == 'POST':
        memorial.delete()
        return redirect('home')
    return render(request, 'delete_memorial.html', {'memorial': memorial})

def add_message(request, memorial_pk):
    memorial = get_object_or_404(Memorial, pk=memorial_pk)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.memorial = memorial
            message.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'author_name': message.author_name,
                    'content': message.content,
                    'created_at': message.created_at.strftime('%b %d, %Y, %I:%M %p')
                })
            return redirect('memorial_detail', pk=memorial.pk)
    
    return redirect('memorial_detail', pk=memorial.pk)

def light_candle(request, memorial_pk):
    memorial = get_object_or_404(Memorial, pk=memorial_pk)
    
    if request.method == 'POST':
        form = CandleForm(request.POST)
        if form.is_valid():
            candle = form.save(commit=False)
            candle.memorial = memorial
            candle.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'lit_by': candle.lit_by,
                    'message': candle.message,
                    'lit_at': candle.lit_at.strftime('%b %d, %Y, %I:%M %p')
                })
            return redirect('memorial_detail', pk=memorial.pk)
    
    return redirect('memorial_detail', pk=memorial.pk)

class SimpleContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea, max_length=2000)

def about(request):
    return render(request, 'about.html')

def contact(request):
    form = SimpleContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        msg = form.cleaned_data['message']
        subject = f"Contact from {name} via Eternal Memories"
        body = f"From: {name} <{email}>\n\n{msg}"
        to_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)
        try:
            if to_email:
                send_mail(subject, body, to_email, [to_email], fail_silently=True)
            else:
                logger.info("Contact message (email not configured): %s", body)
            messages.success(request, "Thank you for reaching out. We’ll get back to you soon.")
            return redirect('contact')
        except BadHeaderError:
            messages.error(request, "Invalid header detected. Please try again.")
    return render(request, 'contact.html', {'form': form})

def privacy(request):
    return render(request, 'privacy.html')
