"""
URL configuration for chats app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    UserViewSet,
    ConversationViewSet,
    MessageViewSet,
    ConversationMessageViewSet
)

app_name = 'chats'

# Create the main router
router = DefaultRouter()

# Register the main viewsets
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Create nested router for conversation messages
conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', ConversationMessageViewSet, basename='conversation-messages')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
    # Additional URL patterns will be added here
]