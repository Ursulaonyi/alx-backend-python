from django.contrib import admin
from .models import Message, Notification, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content', 'timestamp', 'edited', 'edited_at']
    list_filter = ['timestamp', 'edited', 'sender', 'receiver']
    search_fields = ['sender__username', 'receiver__username', 'content']
    ordering = ['-timestamp']
    readonly_fields = ['edited', 'edited_at']


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ['message', 'version', 'edited_by', 'edited_at', 'old_content_preview']
    list_filter = ['edited_at', 'edited_by']
    search_fields = ['message__content', 'old_content', 'edited_by__username']
    ordering = ['-edited_at']
    readonly_fields = ['message', 'old_content', 'edited_by', 'edited_at', 'version']

    def old_content_preview(self, obj):
        return obj.old_content[:50] + "..." if len(obj.old_content) > 50 else obj.old_content
    old_content_preview.short_description = 'Old Content Preview'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'title', 'content']
    ordering = ['-created_at']