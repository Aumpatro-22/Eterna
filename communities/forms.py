from django import forms
from .models import Community, Channel, CommunityMessage

class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'is_public']

class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['name', 'is_public']

class CommunityMessageForm(forms.ModelForm):
    class Meta:
        model = CommunityMessage
        fields = ['content']
        widgets = {'content': forms.Textarea(attrs={'rows': 2})}
