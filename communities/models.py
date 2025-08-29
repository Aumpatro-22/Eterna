from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Community(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_communities')
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:95]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Membership(models.Model):
    ROLE_CHOICES = (('owner', 'Owner'), ('admin', 'Admin'), ('member', 'Member'))
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.community.name}"

class Channel(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='channels')
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:95]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.name} ({self.community.name})"

class CommunityMessage(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"
