from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class UserManager(BaseUserManager):
    """
    Custom user manager for User model with email as the unique identifier.
    """
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not first_name:
            raise ValueError('The First Name field must be set')
        if not last_name:
            raise ValueError('The Last Name field must be set')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, first_name, last_name, password, **extra_fields)


class User(AbstractUser):
    """
    Extended User model with additional fields for the messaging app.
    Extends Django's built-in AbstractUser to add custom fields.
    """
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    
    # Use UUID as primary key
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    
    # Override username to not be required since we're using email
    username = None
    
    # Required fields from specification
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    
    # Additional fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    # Use custom manager
    objects = UserManager()
    
    class Meta:
        db_table = 'chats_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """
    Model representing a conversation between multiple users.
    Tracks participants in the conversation.
    """
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    participants = models.ManyToManyField(
        User, 
        related_name='conversations',
        through='ConversationParticipant'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chats_conversation'
        indexes = [
            models.Index(fields=['conversation_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Conversation {self.conversation_id}"
    
    def get_participants_list(self):
        """Return a list of participant names for display purposes."""
        return [str(participant) for participant in self.participants.all()]


class ConversationParticipant(models.Model):
    """
    Through model for the many-to-many relationship between Conversation and User.
    Allows for additional fields related to participation if needed in the future.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chats_conversation_participant'
        unique_together = ('conversation', 'user')
        indexes = [
            models.Index(fields=['conversation', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user} in {self.conversation}"


class Message(models.Model):
    """
    Model representing a message within a conversation.
    Contains the message content, sender, and conversation reference.
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        db_column='sender_id'
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chats_message'
        ordering = ['-sent_at']  # Most recent messages first
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
            models.Index(fields=['sent_at']),
            models.Index(fields=['conversation', 'sent_at']),  # Compound index for conversation messages
        ]
    
    def __str__(self):
        return f"Message from {self.sender.first_name} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_short_preview(self, max_length=50):
        """Return a shortened version of the message for previews."""
        if len(self.message_body) <= max_length:
            return self.message_body
        return self.message_body[:max_length] + "..."