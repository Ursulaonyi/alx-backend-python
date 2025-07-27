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
from .filters import MessageFilter
from .pagination import MessagePagination, ConversationPagination, UserPagination

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'date_joined']
    ordering = ['-date_joined']
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return []
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if self.action in ['search']:
            return User.objects.all()
        return User.objects.filter(user_id=self.request.user.user_id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'error': 'Query parameter "q" is required'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(user_id=request.user.user_id)[:10]

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    pagination_class = ConversationPagination

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            Prefetch('messages', queryset=Message.objects.select_related('sender'))
        ).distinct().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        elif self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        detail_serializer = ConversationDetailSerializer(
            conversation, 
            context={'request': request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        conversation.participants.add(user)
        return Response({'message': 'User added to conversation'})


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation, IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    pagination_class = MessagePagination
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    search_fields = ['message_body']

    def get_queryset(self):
        return Message.objects.filter(conversation__participants=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        elif self.action == 'list':
            return MessageListSerializer
        return MessageSerializer