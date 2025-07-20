"""
URL configuration for chats app
"""
from django.urls import path, include
from rest_framework_nested import routers

from .views import (
    UserViewSet,
    ConversationViewSet,
    MessageViewSet,
)

app_name = 'chats'

# Create the main router
router = routers.NestedDefaultRouter()

# Register the main viewsets
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# If you need nested routes, you can create them like this:
# Example: /conversations/{conversation_pk}/messages/
conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
    # Additional URL patterns will be added here
]