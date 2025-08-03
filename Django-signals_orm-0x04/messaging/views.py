from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import transaction
from .models import Message, MessageHistory


@login_required
def message_history(request, message_id):
    """Display the edit history of a message."""
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view this message
    if request.user != message.sender and request.user != message.receiver:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get all history entries for this message
    history = MessageHistory.objects.filter(message=message).order_by('-version')
    
    context = {
        'message': message,
        'history': history,
    }
    
    return render(request, 'messaging/message_history.html', context)


@login_required
def message_list(request):
    """Display user's messages with edit indicators."""
    sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
    received_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    
    context = {
        'sent_messages': sent_messages,
        'received_messages': received_messages,
    }
    
    return render(request, 'messaging/message_list.html', context)


@login_required
def delete_user_confirm(request):
    """Show confirmation page for account deletion."""
    if request.method == 'GET':
        # Get user's data summary for confirmation
        sent_count = Message.objects.filter(sender=request.user).count()
        received_count = Message.objects.filter(receiver=request.user).count()
        notification_count = request.user.notifications.count()
        
        context = {
            'sent_messages_count': sent_count,
            'received_messages_count': received_count,
            'notifications_count': notification_count,
        }
        
        return render(request, 'messaging/delete_user_confirm.html', context)


@login_required
def delete_user(request):
    """Delete user account and all related data."""
    if request.method == 'POST':
        # Double-check that the user wants to delete their account
        confirmation = request.POST.get('confirm_delete')
        if confirmation != 'DELETE':
            messages.error(request, 'Please type "DELETE" to confirm account deletion.')
            return redirect('delete_user_confirm')
        
        try:
            user = request.user
            username = user.username
            
            # Use transaction to ensure atomic deletion
            with transaction.atomic():
                # Log out the user first
                logout(request)
                
                # Delete the user (signals will handle related data cleanup)
                user.delete()
                
                messages.success(request, f'Account "{username}" has been successfully deleted.')
                
        except Exception as e:
            messages.error(request, f'Error deleting account: {str(e)}')
            return redirect('delete_user_confirm')
    
    return redirect('message_list')


@login_required
def user_profile(request):
    """Display user profile with account management options."""
    # Get user statistics
    sent_count = Message.objects.filter(sender=request.user).count()
    received_count = Message.objects.filter(receiver=request.user).count()
    notification_count = request.user.notifications.count()
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    
    context = {
        'user': request.user,
        'sent_messages_count': sent_count,
        'received_messages_count': received_count,
        'notifications_count': notification_count,
        'unread_notifications_count': unread_notifications,
    }
    
    return render(request, 'messaging/user_profile.html', context)