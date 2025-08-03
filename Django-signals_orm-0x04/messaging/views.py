from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Prefetch
from .models import Message, MessageHistory, Conversation


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
def conversation_list(request):
    """Display user's conversations with optimized queries."""
    # Get all unique conversation partners
    sent_to = Message.objects.filter(sender=request.user).values_list('receiver', flat=True).distinct()
    received_from = Message.objects.filter(receiver=request.user).values_list('sender', flat=True).distinct()
    
    # Combine and get unique partners
    partner_ids = set(list(sent_to) + list(received_from))
    partners = User.objects.filter(id__in=partner_ids).select_related()
    
    # Get latest message for each conversation using optimized query
    conversations = []
    for partner in partners:
        latest_message = Message.objects.filter(
            Q(sender=request.user, receiver=partner) | 
            Q(sender=partner, receiver=request.user)
        ).select_related('sender', 'receiver').order_by('-timestamp').first()
        
        if latest_message:
            # Count unread messages
            unread_count = Message.objects.filter(
                sender=partner,
                receiver=request.user,
                notifications__is_read=False
            ).count()
            
            conversations.append({
                'partner': partner,
                'latest_message': latest_message,
                'unread_count': unread_count
            })
    
    # Sort by latest message timestamp
    conversations.sort(key=lambda x: x['latest_message'].timestamp, reverse=True)
    
    context = {
        'conversations': conversations,
    }
    
    return render(request, 'messaging/conversation_list.html', context)


@login_required
def threaded_conversation(request, partner_id):
    """Display threaded conversation between current user and partner."""
    partner = get_object_or_404(User, id=partner_id)
    
    # Get all messages in conversation with optimized prefetching
    conversation_messages = Message.objects.get_conversation_messages(request.user, partner)
    
    # Get only top-level messages (not replies)
    top_level_messages = conversation_messages.filter(parent_message__isnull=True)
    
    # Prefetch replies for each top-level message with optimized queries
    top_level_with_replies = top_level_messages.prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver').order_by('timestamp')
        ),
        Prefetch(
            'replies__replies',
            queryset=Message.objects.select_related('sender', 'receiver').order_by('timestamp')
        )
    )
    
    # Build threaded structure
    threaded_messages = []
    for message in top_level_with_replies:
        thread = {
            'message': message,
            'replies': build_reply_tree(message)
        }
        threaded_messages.append(thread)
    
    context = {
        'partner': partner,
        'threaded_messages': threaded_messages,
        'current_user': request.user,
    }
    
    return render(request, 'messaging/threaded_conversation.html', context)


def build_reply_tree(message, max_depth=3):
    """Recursively build reply tree with depth limit to prevent performance issues."""
    if message.thread_level >= max_depth:
        return []
    
    replies = []
    direct_replies = message.get_direct_replies()
    
    for reply in direct_replies:
        reply_data = {
            'message': reply,
            'replies': build_reply_tree(reply, max_depth)
        }
        replies.append(reply_data)
    
    return replies


@login_required
def message_thread(request, message_id):
    """Display a specific message thread with all replies."""
    try:
        # Get message with optimized prefetching
        message = Message.objects.get_message_with_thread(message_id)
        
        # Check permissions
        if request.user != message.sender and request.user != message.receiver:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get the root message of the thread
        root_message = message.get_thread_root()
        
        # Build the complete thread tree
        thread_tree = {
            'message': root_message,
            'replies': build_reply_tree(root_message)
        }
        
        context = {
            'thread_tree': thread_tree,
            'current_message': message,
            'current_user': request.user,
        }
        
        return render(request, 'messaging/message_thread.html', context)
        
    except Message.DoesNotExist:
        messages.error(request, 'Message not found.')
        return redirect('conversation_list')


@login_required
def reply_to_message(request, message_id):
    """Handle replying to a specific message."""
    if request.method == 'POST':
        parent_message = get_object_or_404(Message, id=message_id)
        
        # Check permissions
        if request.user != parent_message.sender and request.user != parent_message.receiver:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        content = request.POST.get('content')
        if not content:
            messages.error(request, 'Reply content cannot be empty.')
            return redirect('message_thread', message_id=message_id)
        
        # Determine receiver (the other participant in the conversation)
        if request.user == parent_message.sender:
            receiver = parent_message.receiver
        else:
            receiver = parent_message.sender
        
        # Create reply
        reply = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            parent_message=parent_message
        )
        
        messages.success(request, 'Reply sent successfully.')
        return redirect('message_thread', message_id=message_id)
    
    return redirect('conversation_list')


@login_required
def message_list(request):
    """Legacy view - redirect to conversation list."""
    return redirect('conversation_list')


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
    
    return redirect('conversation_list')


@login_required
def user_profile(request):
    """Display user profile with account management options."""
    # Get user statistics with optimized queries
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