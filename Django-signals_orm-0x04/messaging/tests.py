from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


class MessageModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')

    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertEqual(message.content, "Test message")
        self.assertFalse(message.edited)

    def test_message_edit_tracking(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )
        self.assertFalse(message.edited)
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # Refresh from database
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertIsNotNone(message.edited_at)


class MessageHistoryTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')

    def test_history_creation_on_edit(self):
        # Create message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )
        
        # No history should exist yet
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 0)
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # History should be created
        history = MessageHistory.objects.filter(message=message).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.edited_by, self.sender)
        self.assertEqual(history.version, 1)

    def test_multiple_edits_create_versions(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Version 1"
        )
        
        # First edit
        message.content = "Version 2"
        message.save()
        
        # Second edit
        message.content = "Version 3"
        message.save()
        
        # Should have 2 history entries
        histories = MessageHistory.objects.filter(message=message).order_by('version')
        self.assertEqual(histories.count(), 2)
        
        self.assertEqual(histories[0].old_content, "Version 1")
        self.assertEqual(histories[0].version, 1)
        
        self.assertEqual(histories[1].old_content, "Version 2")
        self.assertEqual(histories[1].version, 2)


class SignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')

    def test_message_creation_triggers_notification(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this should trigger a notification!"
        )
        
        notification = Notification.objects.filter(message=message).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.receiver)

    def test_message_edit_triggers_history_logging(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message"
        )
        
        # Edit triggers pre_save signal
        message.content = "Edited message"
        message.save()
        
        # Check history was created
        history = MessageHistory.objects.filter(message=message).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, "Original message")