from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

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
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter, ConversationFilter, UserFilter
from .pagination import MessagePagination, ConversationPagination, UserPagination

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    Provides CRUD operations for user management.
    """
    queryset = User.objects.all()
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'date_joined']
    ordering = ['-date_joined']
    pagination_class = UserPagination
    
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
    
    def get_queryset(self):
        """Users can only see their own profile unless it's a search."""
        if self.action in ['search']:
            return User.objects.all()
        return User.objects.filter(user_id=self.request.user.user_id)
    
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
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['title']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    pagination_class = ConversationPagination
    
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
        conversation_id = conversation.conversation_id
        
        # Verify user is participant
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': f'You are not a participant in conversation {conversation_id}'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
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
    Provides endpoints for listing, creating, and managing messages with filtering and pagination.
    """
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    pagination_class = MessagePagination
    
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
    
    def list(self, request, *args, **kwargs):
        """
        List messages with filtering and pagination.
        
        Available filters:
        - conversation_participants: Filter by conversation participants
        - conversation: Filter by specific conversation
        - sender: Filter by message sender
        - sent_at_after/sent_at_before: Filter by datetime range
        - sent_date_after/sent_date_before: Filter by date range
        - message_body: Filter by message content (case-insensitive)
        - conversation_with_user: Filter messages from conversations with specific user
        - is_group_conversation: Filter by conversation type
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Send a new message to a conversation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify user is participant in the conversation
        conversation = serializer.validated_data['conversation']
        conversation_id = conversation.conversation_id
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': f'You are not a participant in conversation {conversation_id}'}, 
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
        conversation_id = message.conversation.conversation_id
        
        # Only allow sender to update their own messages
        if message.sender.user_id != request.user.user_id:
            return Response(
                {'error': f'You can only edit your own messages in conversation {conversation_id}'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a message (only by the sender)."""
        message = self.get_object()
        conversation_id = message.conversation.conversation_id
        
        # Only allow sender to delete their own messages
        if message.sender.user_id != request.user.user_id:
            return Response(
                {'error': f'You can only delete your own messages in conversation {conversation_id}'}, 
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
        """Search messages by content with pagination."""
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(
            message_body__icontains=query
        )
        
        # Apply pagination to search results
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
    
    @action(detail=True, methods=['get'])
    def conversation(self, request, pk=None):
        """Get the conversation that contains this message."""
        message = self.get_object()
        conversation_id = message.conversation.conversation_id
        
        # Verify user is participant in the conversation
        if not message.conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'error': f'You are not a participant in conversation {conversation_id}'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ConversationDetailSerializer(
            message.conversation, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        """
        Get messages filtered by conversation participants or specific users.
        
        Query Parameters:
        - conversation_id: Specific conversation ID
        - user_id: Messages from conversations with this user
        - users: Comma-separated user IDs for conversations with these users
        - page