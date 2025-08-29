from django import forms
from .models import Memorial, Message, Candle

class MemorialForm(forms.ModelForm):
    use_ai_image = forms.BooleanField(
        required=False, 
        label="Generate a symbolic image instead of uploading a photo"
    )
    
    image_prompt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Describe the symbolic image you'd like (we'll create a respectful, soft cartoon-style illustration)."
    )
    
    generate_tribute = forms.BooleanField(
        required=False,
        label="Use AI to help generate a tribute"
    )
    
    relationship = forms.CharField(
        required=False,
        max_length=100,
        help_text="Your relationship with the departed (e.g., parent, friend)"
    )
    
    memories = forms.CharField(
        required=False,
        widget=forms.Textarea,
        help_text="Share some special memories to include in the tribute"
    )
    
    class Meta:
        model = Memorial
        fields = ['name', 'date_of_birth', 'date_of_passing', 'biography', 'tribute', 'image']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_passing': forms.DateInput(attrs={'type': 'date'}),
            'biography': forms.Textarea(attrs={'rows': 5}),
            'tribute': forms.Textarea(attrs={'rows': 5}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['author_name', 'author_email', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }

class CandleForm(forms.ModelForm):
    class Meta:
        model = Candle
        fields = ['lit_by', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2}),
        }
