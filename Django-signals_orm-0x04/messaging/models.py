from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MessageManager(models.Manager):
    """Custom manager for Message model with optimized queries."""
    
    def get_conversation_messages(self, user1, user2):
        return self.select_related('sender', 'receiver', 'parent_message')\
                  .prefetch_related('replies__sender', 'replies__receiver')\
                  .filter(
                      models.Q(sender=user1, receiver=user2) | 
                      models.Q(sender=user2, receiver=user1)
                  ).order_by('timestamp')
    
    def get_threaded_messages(self, conversation_messages):
        return conversation_messages.filter(parent_message__isnull=True)
    
    def get_message_with_thread(self, message_id):
        return self.select_related('sender', 'receiver', 'parent_message')\
                  .prefetch_related(
                      'replies__sender',
                      'replies__receiver', 
                      'replies__replies__sender',
                      'replies__replies__receiver'
                  ).get(id=message_id)


class UnreadMessagesManager(models.Manager):
    """Custom manager to retrieve unread messages for a specific user."""
    
    def for_user(self, user):
        return self.filter(receiver=user, read=False).only('id', 'content', 'sender', 'timestamp')


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    read = models.BooleanField(default=False)  # <- NEW FIELD

    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    
    thread_level = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    
    objects = MessageManager()
    unread = UnreadMessagesManager()  # <- NEW MANAGER

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['sender', 'receiver', 'timestamp']),
            models.Index(fields=['parent_message', 'timestamp']),
            models.Index(fields=['thread_level']),
        ]

    def __str__(self):
        thread_indicator = f" (Reply Level {self.thread_level})" if self.parent_message else ""
        return f"Message from {self.sender.username} to {self.receiver.username}{thread_indicator}"

    def save(self, *args, **kwargs):
        if self.parent_message:
            self.thread_level = self.parent_message.thread_level + 1
            if self.parent_message.sender == self.sender:
                self.receiver = self.parent_message.receiver
            else:
                self.receiver = self.parent_message.sender

        if self.pk:
            original = Message.objects.get(pk=self.pk)
            if original.content != self.content:
                self.edited = True
                self.edited_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        if self.parent_message and not self.pk:
            self.parent_message.reply_count = self.parent_message.replies.count()
            self.parent_message.save(update_fields=['reply_count'])

    def get_thread_root(self):
        if self.parent_message:
            return self.parent_message.get_thread_root()
        return self

    def get_all_replies(self):
        return Message.objects.filter(
            models.Q(parent_message=self) |
            models.Q(parent_message__parent_message=self) |
            models.Q(parent_message__parent_message__parent_message=self)
        ).select_related('sender', 'receiver').order_by('timestamp')

    def get_direct_replies(self):
        return self.replies.select_related('sender', 'receiver').order_by('timestamp')

    def is_reply(self):
        return self.parent_message is not None

    def get_conversation_participants(self):
        root = self.get_thread_root()
        participants = {root.sender, root.receiver}
        for reply in root.get_all_replies():
            participants.add(reply.sender)
            participants.add(reply.receiver)
        return list(participants)


class ConversationManager(models.Manager):
    def get_user_conversations(self, user):
        from django.db.models import Q, Max, Subquery, OuterRef
        latest_messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).values('sender', 'receiver').annotate(
            latest_timestamp=Max('timestamp')
        ).values_list('latest_timestamp', flat=True)
        
        return Message.objects.filter(
            timestamp__in=Subquery(latest_messages)
        ).select_related('sender', 'receiver').order_by('-timestamp')


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now)
    last_message_at = models.DateTimeField(default=timezone.now)
    message_count = models.PositiveIntegerField(default=0)
    
    objects = ConversationManager()
    
    class Meta:
        ordering = ['-last_message_at']
    
    def __str__(self):
        participant_names = ", ".join([p.username for p in self.participants.all()[:2]])
        return f"Conversation: {participant_names}"
    
    def update_last_message(self):
        latest_message = Message.objects.filter(
            models.Q(sender__in=self.participants.all()) & 
            models.Q(receiver__in=self.participants.all())
        ).order_by('-timestamp').first()
        
        if latest_message:
            self.last_message_at = latest_message.timestamp
            self.message_count = Message.objects.filter(
                models.Q(sender__in=self.participants.all()) & 
                models.Q(receiver__in=self.participants.all())
            ).count()
            self.save(update_fields=['last_message_at', 'message_count'])


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    edited_at = models.DateTimeField(default=timezone.now)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-edited_at']
        verbose_name = "Message History"
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f"Version {self.version} of message {self.message.id}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
