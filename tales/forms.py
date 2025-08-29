from django import forms
from .models import Tale, Chapter

class TaleForm(forms.ModelForm):
    class Meta:
        model = Tale
        fields = ['title', 'subtitle', 'description', 'is_public']

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['order', 'title', 'content', 'published']
        widgets = {'content': forms.Textarea(attrs={'rows': 10})}
