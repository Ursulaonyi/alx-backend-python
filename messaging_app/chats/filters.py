import django_filters
from .models import Message, Conversation
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageFilter(django_filters.FilterSet):
    conversation_participants = django_filters.ModelMultipleChoiceFilter(
        field_name='conversation__participants',
        queryset=User.objects.all()
    )
    conversation = django_filters.ModelChoiceFilter(
        queryset=Conversation.objects.all()
    )
    sender = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    sent_at_after = django_filters.DateTimeFilter(
        field_name='sent_at', lookup_expr='gte'
    )
    sent_at_before = django_filters.DateTimeFilter(
        field_name='sent_at', lookup_expr='lte'
    )
    sent_date_after = django_filters.DateFilter(
        field_name='sent_at', lookup_expr='date__gte'
    )
    sent_date_before = django_filters.DateFilter(
        field_name='sent_at', lookup_expr='date__lte'
    )
    message_body = django_filters.CharFilter(
        field_name='message_body', lookup_expr='icontains'
    )
    message_body_exact = django_filters.CharFilter(
        field_name='message_body', lookup_expr='exact'
    )
    conversation_with_user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(), method='filter_conversation_with_user'
    )
    is_group_conversation = django_filters.BooleanFilter(
        field_name='conversation__is_group_chat'
    )

    class Meta:
        model = Message
        fields = {
            'message_id': ['exact'],
            'sent_at': ['exact', 'gte', 'lte', 'year', 'month', 'day']
        }

    def filter_conversation_with_user(self, queryset, name, value):
        if value:
            return queryset.filter(conversation__participants=value)
        return queryset
