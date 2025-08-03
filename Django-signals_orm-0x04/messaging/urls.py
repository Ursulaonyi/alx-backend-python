from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('conversation/<int:partner_id>/', views.threaded_conversation, name='threaded_conversation'),
    path('thread/<int:message_id>/', views.message_thread, name='message_thread'),
    path('reply/<int:message_id>/', views.reply_to_message, name='reply_to_message'),
    path('history/<int:message_id>/', views.message_history, name='message_history'),
    path('messages/', views.message_list, name='message_list'),  # Legacy redirect
    path('profile/', views.user_profile, name='user_profile'),
    path('delete-account/', views.delete_user_confirm, name='delete_user_confirm'),
    path('delete-account/confirm/', views.delete_user, name='delete_user'),
]