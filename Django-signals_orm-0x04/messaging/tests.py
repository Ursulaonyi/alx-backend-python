from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification


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

    def test_message_str(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        expected_str = f"Message from {self.sender.username} to {self.receiver.username}"
        self.assertEqual(str(message), expected_str)


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            content='Test content'
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, 'Test Notification')
        self.assertFalse(notification.is_read)

    def test_notification_str(self):
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            content='Test content'
        )
        expected_str = f"Notification for {self.user.username}: Test Notification"
        self.assertEqual(str(notification), expected_str)


class SignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')

    def test_message_creation_triggers_notification(self):
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this should trigger a notification!"
        )
        
        # Check that a notification was created
        notification = Notification.objects.filter(message=message).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertIn(self.sender.username, notification.title)

    def test_self_message_no_notification(self):
        # User messages themselves
        Message.objects.create(
            sender=self.sender,
            receiver=self.sender,
            content="Note to self"
        )
        
        # Should not create notification
        notifications = Notification.objects.filter(user=self.sender)
        self.assertEqual(notifications.count(), 0)