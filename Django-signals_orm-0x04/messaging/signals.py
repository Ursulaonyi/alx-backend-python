from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Create a notification when a new message is saved."""
    if created and instance.sender != instance.receiver:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            title=f"New message from {instance.sender.username}",
            content=f"You have received a new message: {instance.content[:50]}..."
        )


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """Log message content before it's updated."""
    if instance.pk:  # Only for existing messages (updates)
        try:
            original = Message.objects.get(pk=instance.pk)
            # Check if content is actually changing
            if original.content != instance.content:
                # Get the next version number
                last_history = MessageHistory.objects.filter(message=original).order_by('-version').first()
                next_version = (last_history.version + 1) if last_history else 1
                
                # Create history entry with old content
                MessageHistory.objects.create(
                    message=original,
                    old_content=original.content,
                    edited_by=instance.sender,  # Assuming sender is the one editing
                    version=next_version
                )
        except Message.DoesNotExist:
            # Message doesn't exist yet, skip logging
            pass