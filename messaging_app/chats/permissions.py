"""
Custom permissions for the messaging app
"""
from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only authenticated users to access the API
    and only participants in a conversation to send, view, update and delete messages
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is a participant of the conversation
        """
        # For message objects, check if user is participant of the conversation
        if hasattr(obj, 'conversation') and hasattr(obj.conversation, 'participants'):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        # For conversation objects, check if user is a participant
        if hasattr(obj, 'participants'):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # For user objects, check if it's the same user (using user_id if available)
        if hasattr(obj, 'user_id'):  # Custom User model with user_id field
            return obj.user_id == request.user.user_id
        elif hasattr(obj, 'username'):  # Standard User model
            return obj == request.user
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission for conversations - only participants can view/edit
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        return request.user in obj.participants.all()


class IsMessageOwnerOrConversationParticipant(permissions.BasePermission):
    """
    Custom permission for messages - only message sender or conversation participants can access
    """
    
    def has_object_permission(self, request, view, obj):
        # Message sender can always access their own messages
        if hasattr(obj, 'sender') and obj.sender == request.user:
            return True
        
        # Conversation participants can read messages
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()
        
        # Only message sender can edit/delete their messages
        return obj.sender == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or obj == request.user


class IsUserOwner(permissions.BasePermission):
    """
    Custom permission for user-related operations
    """
    
    def has_object_permission(self, request, view, obj):
        # Users can only access their own profile
        return obj == request.user


class IsConversationParticipant(permissions.BasePermission):
    """
    Permission to check if user is a participant in a conversation
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # For conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # For message objects, check the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False


class CanCreateMessage(permissions.BasePermission):
    """
    Permission to check if user can create a message in a conversation
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if creating a message
        if request.method == 'POST':
            conversation_id = request.data.get('conversation')
            if conversation_id:
                try:
                    from .models import Conversation
                    conversation = Conversation.objects.get(id=conversation_id)
                    return conversation.participants.filter(user_id=request.user.user_id).exists()
                except Conversation.DoesNotExist:
                    return False
        
        return True