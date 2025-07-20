"""
URL configuration for chats app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    ConversationViewSet,
    MessageViewSet,
)

app_name = 'chats'

# Create the main router
router = DefaultRouter()

# Register the main viewsets
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    # Additional URL patterns will be added here
]