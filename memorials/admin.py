from django.contrib import admin
from .models import Memorial, Message, Candle

@admin.register(Memorial)
class MemorialAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at')
    search_fields = ('name', 'biography', 'tribute')
    list_filter = ('created_at', 'is_ai_generated_image')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'memorial', 'created_at')
    search_fields = ('content', 'author_name', 'author_email')
    list_filter = ('created_at',)

@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    list_display = ('lit_by', 'memorial', 'lit_at')
    search_fields = ('message', 'lit_by')
    list_filter = ('lit_at',)
