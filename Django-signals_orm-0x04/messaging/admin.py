from django.contrib import admin
from .models import Message, Notification, MessageHistory, Conversation


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'sender', 'receiver', 'content_preview', 'parent_message', 
        'thread_level', 'reply_count', 'timestamp', 'edited'
    ]
    list_filter = ['timestamp', 'edited', 'thread_level', 'sender', 'receiver']
    search_fields = ['sender__username', 'receiver__username', 'content']
    ordering = ['-timestamp']
    readonly_fields = ['edited', 'edited_at', 'thread_level', 'reply_count']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


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


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'participants_list', 'message_count', 'last_message_at']
    list_filter = ['created_at', 'last_message_at']
    search_fields = ['participants__username']
    readonly_fields = ['created_at', 'last_message_at', 'message_count']
    
    def participants_list(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])
    participants_list.short_description = 'Participants'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'title', 'content']
    ordering = ['-created_at']