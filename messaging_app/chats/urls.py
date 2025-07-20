"""
URL configuration for chats app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'chats'

# Router for ViewSets (to be added later)
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    # Additional URL patterns will be added here
]