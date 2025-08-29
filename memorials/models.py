import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class Memorial(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_memorials')
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_passing = models.DateField(null=True, blank=True)
    biography = models.TextField()
    tribute = models.TextField(blank=True)
    
    # Image can be either uploaded or AI-generated
    image = models.ImageField(upload_to='memorial_images/', null=True, blank=True)
    is_ai_generated_image = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    public_id = models.CharField(max_length=22, unique=True, db_index=True, blank=True)  # short UUID-like id
    
    def __str__(self):
        return f"Memorial for {self.name}"
        
    def save(self, *args, **kwargs):
        # Generate a public_id only if it hasn't been set
        if not self.public_id:
            # use urlsafe base64-ish without dashes for shareable IDs
            self.public_id = uuid.uuid4().hex[:22]
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        # Resolve by public id for stable links
        return reverse('memorial_detail_by_id', kwargs={'public_id': self.public_id})

class Message(models.Model):
    memorial = models.ForeignKey(Memorial, on_delete=models.CASCADE, related_name='messages')
    author_name = models.CharField(max_length=255)
    author_email = models.EmailField(blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.author_name} on {self.memorial.name}'s memorial"

class Candle(models.Model):
    memorial = models.ForeignKey(Memorial, on_delete=models.CASCADE, related_name='candles')
    lit_by = models.CharField(max_length=255)
    lit_at = models.DateTimeField(default=timezone.now)
    message = models.TextField(blank=True)
    
    def __str__(self):
        return f"Candle lit by {self.lit_by} on {self.memorial.name}'s memorial"
