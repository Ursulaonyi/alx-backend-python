"""
Custom filters for the messaging app
"""
import django_filters
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Message, Conversation

User = get_user_model()


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for Message model to enable filtering by:
    - Conversation participants (specific users)
    - Messages within a time range
    - Message content
    - Sender
    """
    
    # Filter by conversation participants
    conversation_participants = django_filters.ModelMultipleChoiceFilter(
        field_name='conversation__participants',
        queryset=User.objects.all(),
        help_text="Filter messages from conversations with specific participants"
    )
    
    # Filter by specific conversation
    conversation = django_filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        help_text="Filter messages from a specific conversation"
    )
    
    # Filter by sender
    sender = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        help_text="Filter messages by sender"
    )
    
    # Filter by time range
    sent_at_after = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        help_text="Filter messages sent after this datetime (ISO format: YYYY-MM-DDTHH:MM:SS)"
    )
    
    sent_at_before = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        help_text="Filter messages sent before this datetime (ISO format: YYYY-MM-DDTHH:MM:SS)"
    )
    
    # Filter by date range (date only)
    sent_date_after = django_filters.DateFilter(
        field_name='sent_at__date',
        lookup_expr='gte',
        help_text="Filter messages sent after this date (YYYY-MM-DD)"
    )
    
    sent_date_before = django_filters.DateFilter(
        field_name='sent_at__date',
        lookup_expr='lte',
        help_text="Filter messages sent before this date (YYYY-MM-DD)"
    )
    
    # Filter by message content
    message_body = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filter messages containing specific text (case-insensitive)"
    )
    
    # Filter by message content with exact match
    message_body_exact = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='exact',
        help_text="Filter messages with exact text match"
    )
    
    # Custom filter for conversations with specific user
    conversation_with_user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        method='filter_conversation_with_user',
        help_text="Filter messages from conversations that include a specific user"
    )
    
    # Filter by conversation type (group or direct)
    is_group_conversation = django_filters.BooleanFilter(
        field_name='conversation__is_group_chat',
        help_text="Filter messages from group conversations (true) or direct conversations (false)"
    )
    
    class Meta:
        model = Message
        fields = {
            'message_id': ['exact'],
            'sent_at': ['exact', 'gte', 'lte', 'year', 'month', 'day'],
            'updated_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_conversation_with_user(self, queryset, name, value):
        """
        Custom filter method to get messages from conversations 
        that include a specific user as participant
        """
        if value:
            return queryset.filter(conversation__participants=value)
        return queryset


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for Conversation model
    """
    
    # Filter by participants
    participants = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        help_text="Filter conversations with specific participants"
    )
    
    # Filter by conversation type
    is_group_chat = django_filters.BooleanFilter(
        help_text="Filter by conversation type: true for group chats, false for direct messages"
    )
    
    # Filter by creation date range
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter conversations created after this datetime"
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter conversations created before this datetime"
    )
    
    # Filter by title (for group chats)
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Filter conversations by title (case-insensitive)"
    )
    
    # Custom filter for conversations with specific user
    with_user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        method='filter_with_user',
        help_text="Filter conversations that include a specific user"
    )
    
    # Filter conversations with recent activity
    has_recent_messages = django_filters.BooleanFilter(
        method='filter_has_recent_messages',
        help_text="Filter conversations with messages in the last 24 hours"
    )
    
    class Meta:
        model = Conversation
        fields = {
            'conversation_id': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_with_user(self, queryset, name, value):
        """
        Filter conversations that include a specific user as participant
        """
        if value:
            return queryset.filter(participants=value)
        return queryset
    
    def filter_has_recent_messages(self, queryset, name, value):
        """
        Filter conversations with recent messages (last 24 hours)
        """
        if value is True:
            from django.utils import timezone
            from datetime import timedelta
            
            recent_time = timezone.now() - timedelta(hours=24)
            return queryset.filter(messages__sent_at__gte=recent_time).distinct()
        elif value is False:
            from django.utils import timezone
            from datetime import timedelta
            
            recent_time = timezone.now() - timedelta(hours=24)
            return queryset.exclude(messages__sent_at__gte=recent_time).distinct()
        return queryset


class UserFilter(django_filters.FilterSet):
    """
    Filter class for User model
    """
    
    # Filter by name
    name = django_filters.CharFilter(
        method='filter_by_name',
        help_text="Filter users by first name or last name (case-insensitive)"
    )
    
    # Filter by email domain
    email_domain = django_filters.CharFilter(
        method='filter_email_domain',
        help_text="Filter users by email domain (e.g., 'gmail.com')"
    )
    
    # Filter by date joined range
    joined_after = django_filters.DateFilter(
        field_name='date_joined__date',
        lookup_expr='gte',
        help_text="Filter users who joined after this date"
    )
    
    joined_before = django_filters.DateFilter(
        field_name='date_joined__date',
        lookup_expr='lte',
        help_text="Filter users who joined before this date"
    )
    
    class Meta:
        model = User
        fields = {
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'is_active': ['exact'],
            'date_joined': ['exact', 'gte', 'lte'],
        }
    
    def filter_by_name(self, queryset, name, value):
        """
        Filter users by first name or last name
        """
        if value:
            return queryset.filter(
                Q(first_name__icontains=value) | Q(last_name__icontains=value)
            )
        return queryset
    
    def filter_email_domain(self, queryset, name, value):
        """
        Filter users by email domain
        """
        if value:
            return queryset.filter(email__iendswith=f'@{value}')
        return queryset