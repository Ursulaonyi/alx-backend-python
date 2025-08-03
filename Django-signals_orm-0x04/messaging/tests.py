from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
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
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # History should be created
        history = MessageHistory.objects.filter(message=message).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.edited_by, self.sender)
        self.assertEqual(history.version, 1)


class UserDeletionSignalTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')

    def test_user_deletion_cleans_up_messages(self):
        # Create messages
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message from user1 to user2"
        )
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message from user2 to user1"
        )
        
        # Verify messages exist
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(Notification.objects.count(), 2)  # Notifications created by signals
        
        # Delete user1
        self.user1.delete()
        
        # Check that messages involving user1 are deleted
        remaining_messages = Message.objects.all()
        self.assertEqual(remaining_messages.count(), 0)  # All messages should be deleted
        
        # Check that notifications are cleaned up
        remaining_notifications = Notification.objects.all()
        self.assertEqual(remaining_notifications.count(), 0)

    def test_user_deletion_cleans_up_message_histories(self):
        # Create and edit a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # Edit the message to create history
        message.content = "Edited content"
        message.save()
        
        # Verify history exists
        self.assertEqual(MessageHistory.objects.count(), 1)
        
        # Delete user1
        self.user1.delete()
        
        # Check that history is cleaned up
        self.assertEqual(MessageHistory.objects.count(), 0)


class UserDeletionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_delete_user_confirm_view_requires_login(self):
        response = self.client.get(reverse('delete_user_confirm'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_delete_user_confirm_view_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('delete_user_confirm'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirm Account Deletion')

    def test_delete_user_view_with_correct_confirmation(self):
        self.client.login(username='testuser', password='testpass')
        
        # Create some data for the user
        other_user = User.objects.create_user(username='other', password='testpass')
        Message.objects.create(
            sender=self.user,
            receiver=other_user,
            content="Test message"
        )
        
        # Verify user and data exist
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertEqual(Message.objects.count(), 1)
        
        # Delete user with correct confirmation
        response = self.client.post(reverse('delete_user'), {
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