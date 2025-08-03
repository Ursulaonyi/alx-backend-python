from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
import logging

logger = logging.getLogger(__name__)


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


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up all user-related data when a user is deleted.
    This signal handles any remaining data that wasn't deleted by CASCADE.
    """
    try:
        # Log the cleanup process
        logger.info(f"Starting cleanup for deleted user: {instance.username}")
        
        # Get counts before deletion for logging
        sent_messages = Message.objects.filter(sender=instance).count()
        received_messages = Message.objects.filter(receiver=instance).count()
        user_notifications = Notification.objects.filter(user=instance).count()
        user_histories = MessageHistory.objects.filter(edited_by=instance).count()
        
        # Delete sent messages (this will cascade to related notifications and histories)
        Message.objects.filter(sender=instance).delete()
        
        # Delete received messages (this will cascade to related notifications and histories)
        Message.objects.filter(receiver=instance).delete()
        
        # Delete any remaining notifications
        Notification.objects.filter(user=instance).delete()
        
        # Delete any remaining message histories where user was the editor
        MessageHistory.objects.filter(edited_by=instance).delete()
        
        # Log successful cleanup
        logger.info(
            f"Successfully cleaned up data for user {instance.username}: "
            f"{sent_messages} sent messages, {received_messages} received messages, "
            f"{user_notifications} notifications, {user_histories} edit histories"
        )
        
    except Exception as e:
        logger.error(f"Error during user data cleanup for {instance.username}: {str(e)}")


@receiver(post_delete, sender=Message)
def cleanup_message_orphans(sender, instance, **kwargs):
    """
    Clean up any orphaned notifications or histories when a message is deleted.
    This provides additional safety beyond CASCADE relationships.
    """
    try:
        # Clean up any orphaned notifications (should be handled by CASCADE, but extra safety)
        orphaned_notifications = Notification.objects.filter(message_id=instance.id)
        notification_count = orphaned_notifications.count()
        if notification_count > 0:
            orphaned_notifications.delete()
            logger.info(f"Cleaned up {notification_count} orphaned notifications for message {instance.id}")
        
        # Clean up any orphaned message histories (should be handled by CASCADE, but extra safety)
        orphaned_histories = MessageHistory.objects.filter(message_id=instance.id)
        history_count = orphaned_histories.count()
        if history_count > 0:
            orphaned_histories.delete()
            logger.info(f"Cleaned up {history_count} orphaned histories for message {instance.id}")
            
    except Exception as e:
        logger.error(f"Error during message cleanup for message {instance.id}: {str(e)}")