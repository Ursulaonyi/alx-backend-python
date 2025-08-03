from django.urls import path
from . import views

urlpatterns = [
    path('', views.message_list, name='message_list'),
    path('history/<int:message_id>/', views.message_history, name='message_history'),
]