from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from .models import Message, Notification, MessageHistory, Conversation


class ThreadedMessageModelTest(TestCase):
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
        self.assertEqual(message.thread_level, 0)
        self.assertIsNone(message.parent_message)

    def test_threaded_message_creation(self):
        # Create parent message
        parent = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message"
        )
        
        # Create reply
        reply = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply to parent",
            parent_message=parent
        )
        
        self.assertEqual(reply.parent_message, parent)
        self.assertEqual(reply.thread_level, 1)
        # Refresh parent to get updated reply count
        parent.refresh_from_db()
        self.assertEqual(parent.reply_count, 1)

    def test_nested_replies(self):
        # Create parent message
        parent = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message"
        )
        
        # Create first level reply
        reply1 = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="First reply",
            parent_message=parent
        )
        
        # Create second level reply
        reply2 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Reply to reply",
            parent_message=reply1
        )
        
        self.assertEqual(reply1.thread_level, 1)
        self.assertEqual(reply2.thread_level, 2)
        self.assertEqual(reply2.get_thread_root(), parent)

    def test_get_all_replies(self):
        parent = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message"
        )
        
        reply1 = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="First reply",
            parent_message=parent
        )
        
        reply2 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Second reply",
            parent_message=reply1
        )
        
        all_replies = parent.get_all_replies()
        self.assertEqual(all_replies.count(), 2)
        self.assertIn(reply1, all_replies)
        self.assertIn(reply2, all_replies)


class MessageManagerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        self.user3 = User.objects.create_user(username='user3', password='testpass')

    def test_get_conversation_messages(self):
        # Create messages between user1 and user2
        msg1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello user2"
        )
        msg2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Hi user1"
        )
        # Create message between user1 and user3 (should not be included)
        msg3 = Message.objects.create(
            sender=self.user1,
            receiver=self.user3,
            content="Hello user3"
        )
        
        conversation = Message.objects.get_conversation_messages(self.user1, self.user2)
        self.assertEqual(conversation.count(), 2)
        self.assertIn(msg1, conversation)
        self.assertIn(msg2, conversation)
        self.assertNotIn(msg3, conversation)

    def test_get_threaded_messages(self):
        # Create parent message
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent message"
        )
        
        # Create reply
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply",
            parent_message=parent
        )
        
        conversation = Message.objects.get_conversation_messages(self.user1, self.user2)
        threaded = Message.objects.get_threaded_messages(conversation)
        
        self.assertEqual(threaded.count(), 1)  # Only parent message
        self.assertIn(parent, threaded)
        self.assertNotIn(reply, threaded)

    def test_get_message_with_thread(self):
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent message"
        )
        
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply",
            parent_message=parent
        )
        
        # Test that optimized query works
        message_with_thread = Message.objects.get_message_with_thread(parent.id)
        self.assertEqual(message_with_thread, parent)
        
        # Access related data (should be prefetched)
        self.assertEqual(message_with_thread.sender.username, 'user1')
        self.assertEqual(message_with_thread.replies.count(), 1)


class ThreadedConversationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')

    def test_conversation_list_view(self):
        self.client.login(username='user1', password='testpass')
        
        # Create a message
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello"
        )
        
        response = self.client.get(reverse('conversation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user2')

    def test_threaded_conversation_view(self):
        self.client.login(username='user1', password='testpass')
        
        # Create parent and reply
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent message"
        )
        
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply message",
            parent_message=parent
        )
        
        response = self.client.get(reverse('threaded_conversation', kwargs={'partner_id': self.user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Parent message')
        self.assertContains(response, 'Reply message')

    def test_reply_to_message(self):
        self.client.login(username='user1', password='testpass')
        
        # Create parent message
        parent = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Original message"
        )
        
        # Reply to the message
        response = self.client.post(reverse('reply_to_message', kwargs={'message_id': parent.id}), {
            'content': 'My reply'
        })
        
        # Should redirect after successful reply
        self.assertEqual(response.status_code, 302)
        
        # Check that reply was created
        reply = Message.objects.filter(parent_message=parent).first()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.content, 'My reply')
        self.assertEqual(reply.sender, self.user1)
        self.assertEqual(reply.thread_level, 1)


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

    def test_reply_triggers_notification(self):
        # Create parent message
        parent = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Parent message"
        )
        
        # Create reply (should trigger notification)
        reply = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Reply message",
            parent_message=parent
        )
        
        # Check notifications were created for both messages
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 2)  # One for parent, one for reply

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


class PerformanceTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', passwor