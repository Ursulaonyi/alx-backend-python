from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification


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
        