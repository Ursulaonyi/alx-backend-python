from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message, ConversationParticipant

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with basic user information.
    Used for general user display and authentication.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 
            'first_name', 
            'last_name', 
            'full_name',
            'email', 
            'phone_number', 
            'role', 
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
    
    def get_full_name(self, obj):
        """Return the user's full name."""
        return f"{obj.first_name} {obj.last_name}"


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users with password handling.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name', 
            'email', 
            'phone_number', 
            'role', 
            'password',
            'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        """Create user with encrypted password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model with sender information.
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id', 
            'conversation',
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def create(self, validated_data):
        """Create message with sender from request context."""
        # Get sender from request if not provided
        if 'sender_id' not in validated_data:
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                validated_data['sender'] = request.user
        else:
            sender_id = validated_data.pop('sender_id')
            validated_data['sender_id'] = sender_id
        
        return super().create(validated_data)


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating messages.
    """
    class Meta:
        model = Message
        fields = ['conversation', 'message_body']
    
    def create(self, validated_data):
        """Create message with sender from request context."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['sender'] = request.user
        return super().create(validated_data)


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for ConversationParticipant model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ConversationParticipant
        fields = ['user', 'joined_at']
        read_only_fields = ['joined_at']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Conversation model.
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_count',
            'last_message',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_participant_count(self, obj):
        """Return the number of participants in the conversation."""
        return obj.participants.count()
    
    def get_last_message(self, obj):
        """Return the last message in the conversation."""
        last_message = obj.messages.first()  # Already ordered by -sent_at in model
        if last_message:
            return {
                'message_id': last_message.message_id,
                'sender': UserSerializer(last_message.sender).data,
                'message_body': last_message.get_short_preview(),
                'sent_at': last_message.sent_at
            }
        return None


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Conversation model with nested messages.
    Used for retrieving conversation details with full message history.
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_details = ConversationParticipantSerializer(
        source='conversationparticipant_set',
        many=True,
        read_only=True
    )
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_details',
            'messages',
            'message_count',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_message_count(self, obj):
        """Return the total number of messages in the conversation."""
        return obj.messages.count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new conversations.
    """
    participants = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        help_text="List of user IDs to add as participants"
    )
    
    class Meta:
        model = Conversation
        fields = ['participants']
    
    def create(self, validated_data):
        """Create conversation and add participants."""
        participant_ids = validated_data.pop('participants')
        
        # Create conversation
        conversation = Conversation.objects.create()
        
        # Add creator as participant if authenticated
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            participant_ids.append(request.user.user_id)
        
        # Add participants
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.set(participants)
        
        return conversation
    
    def validate_participants(self, value):
        """Validate that participants exist and conversation has at least 2 participants."""
        if len(value) < 1:
            raise serializers.ValidationError(
                "A conversation must have at least 2 participants (including yourself)."
            )
        
        # Check if all users exist
        existing_users = User.objects.filter(user_id__in=value).count()
        if existing_users != len(value):
            raise serializers.ValidationError("One or more participant IDs are invalid.")
        
        return value


# Utility serializers for specific use cases

class ConversationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing conversations.
    """
    participants = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'last_message_preview',
            'unread_count',
            'created_at'
        ]
    
    def get_participants(self, obj):
        """Return participant names (excluding current user)."""
        request = self.context.get('request')
        participants = obj.participants.all()
        
        if request and request.user.is_authenticated:
            participants = participants.exclude(user_id=request.user.user_id)
        
        return [f"{p.first_name} {p.last_name}" for p in participants[:3]]  # Limit to 3 names
    
    def get_last_message_preview(self, obj):
        """Return a preview of the last message."""
        last_message = obj.messages.first()
        return last_message.get_short_preview() if last_message else "No messages yet"
    
    def get_unread_count(self, obj):
        """Return unread message count (placeholder for future implementation)."""
        # This would require a read status tracking system
        return 0


class MessageListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing messages in a conversation.
    """
    sender_name = serializers.SerializerMethodField()
    is_own_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender_name',
            'is_own_message',
            'message_body',
            'sent_at'
        ]
    
    def get_sender_name(self, obj):
        """Return sender's full name."""
        return f"{obj.sender.first_name} {obj.sender.last_name}"
    
    def get_is_own_message(self, obj):
        """Check if message belongs to current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender.user_id == request.user.user_id
        return False