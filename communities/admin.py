from django.contrib import admin
from .models import Community, Membership, Channel, CommunityMessage

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_public', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_public', 'created_at')

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('community', 'user', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('community__name', 'user__username')

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'community__name')

@admin.register(CommunityMessage)
class CommunityMessageAdmin(admin.ModelAdmin):
    list_display = ('channel', 'author', 'created_at')
    search_fields = ('content', 'author__username', 'channel__name')
    list_filter = ('created_at',)
