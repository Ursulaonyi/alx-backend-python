from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

    def save(self, *args, **kwargs):
        # If this is an update (not creation) and content changed, mark as edited
        if self.pk:
            original = Message.objects.get(pk=self.pk)
            if original.content != self.content:
                self.edited = True
                self.edited_at = timezone.now()
        super().save(*args, **kwargs)


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