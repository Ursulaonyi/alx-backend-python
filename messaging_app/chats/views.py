from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from django.contrib.auth import get_user_model

from .models import Conversation, Message, ConversationParticipant
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    ConversationSerializer,
    ConversationDetailSerializer,
    ConversationCreateSerializer,
    ConversationListSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageListSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    Provides CRUD operations for user management.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Allow registration without authentication."""
        if self.action == 'create':
            return []  # No authentication required for user registration
        return [permission() for permission in self.permission_classes]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by name or email."""
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(user_id=request.user.user_id)[:10]  # Limit to 10 results
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides endpoints for listing, creating, and managing conversations.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return conversations where the current user is a participant."""
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            Prefetch('messages', queryset=Message.objects.select_related('sender'))
        ).distinct().order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ConversationCreateSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        elif self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new conversation with participants."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation = serializer.save()
        
        # Return detailed conversation data
        detail_serializer = ConversationDetailSerializer(
            conversation, 
            context={'request': request}
        )
        return Response(
            detail_serializer.data, 
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to an existing conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is already a participant
        if conversation.participants.filter(user_id=user_id).exists():
            return Response(
                {'error': 'User is already a participant'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.participants.add(user)
        
        serializer = ConversationDetailSerializer(
            conversation, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from a conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent removing self if it's the last participant
        if (str(user_id) == str(request.user.user_id) and 
            conversation.participants.count() == 1):
            return Response(
                {'error': 'Cannot remove the last participant'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.participants.remove(user_id)
        
        # If no participants left, delete conversation
        if conversation.participants.count() == 0:
            conversation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = ConversationDetailSerializer(
            conversation, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get paginated messages for a specific conversation."""
        conversation = self.get_object()
        messages = conversation.messages.select_related('sender').all()
        
        # Apply pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageListSerializer(
                page, 
                many=True, 
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageListSerializer(
            messages, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent conversations with last message info."""
        conversations = self.get_queryset()[:10]  # Last 10 conversations
        serializer = ConversationListSerializer(
            conversations, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Provides endpoints for listing, creating, and managing messages.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return messages from conversations where user is a participant."""
        user_conversations = Conversation.objects.filter(
            participants=self.request.user
        )
        
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation').order_by('-sent_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return MessageCreateSerializer
        elif self.action == 'list':
            return MessageListSerializer
        return MessageSerializer
    
    def create(self, request, *args, **kwargs):
        """Send a new message to a conversation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify user is participant in the conversation
        conversation = serializer.validated_data['conversation']
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': 'You are not a participant in this conversation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        message = serializer.save()
        
        # Return full message data
        detail_serializer = MessageSerializer(
            message, 
            context={'request': request}
        )
        return Response(
            detail_serializer.data, 
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Update a message (only by the sender)."""
        message = self.get_object()
        
        # Only allow sender to update their own messages
        if message.sender.user_id != request.user.user_id:
            return Response(
                {'error': 'You can only edit your own messages'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a message (only by the sender)."""
        message = self.get_object()
        
        # Only allow sender to delete their own messages
        if message.sender.user_id != request.user.user_id:
            return Response(
                {'error': 'You can only delete your own messages'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent messages across all conversations."""
        messages = self.get_queryset()[:20]  # Last 20 messages
        serializer = MessageListSerializer(
            messages, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search messages by content."""
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(
            message_body__icontains=query
        )[:50]  # Limit to 50 results
        
        serializer = MessageListSerializer(
            messages, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def conversation(self, request, pk=None):
        """Get the conversation that contains this message."""
        message = self.get_object()
        serializer = ConversationDetailSerializer(
            message.conversation, 
            context={'request': request}
        )
        return Response(serializer.data)


# Additional utility views

class ConversationMessageViewSet(viewsets.ModelViewSet):
    """
    Nested viewset for managing messages within a specific conversation.
    Accessed via /conversations/{id}/messages/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_conversation(self):
        """Get the conversation from URL parameters."""
        conversation_id = self.kwargs['conversation_pk']
        return get_object_or_404(
            Conversation.objects.filter(participants=self.request.user),
            conversation_id=conversation_id
        )
    
    def get_queryset(self):
        """Return messages for the specific conversation."""
        conversation = self.get_conversation()
        return Message.objects.filter(
            conversation=conversation
        ).select_related('sender').order_by('-sent_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return MessageCreateSerializer
        elif self.action == 'list':
            return MessageListSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        """Create message in the specific conversation."""
        conversation = self.get_conversation()
        serializer.save(conversation=conversation)