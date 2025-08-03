from django.contrib import admin
from .models import Message, Notification


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content', 'timestamp']
    list_filter = ['timestamp', 'sender', 'receiver']
    search_fields = ['sender__username', 'receiver__username', 'content']
    ordering = ['-timestamp']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'title', 'content']
    ordering = ['-created_at']