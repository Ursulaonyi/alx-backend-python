from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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