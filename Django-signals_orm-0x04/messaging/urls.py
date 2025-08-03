from django.urls import path
from . import views

urlpatterns = [
    path('', views.message_list, name='message_list'),
    path('history/<int:message_id>/', views.message_history, name='message_history'),
    path('profile/', views.user_profile, name='user_profile'),
    path('delete-account/', views.delete_user_confirm, name='delete_user_confirm'),
    path('delete-account/confirm/', views.delete_user, name='delete_user'),
]