from django.urls import path
from . import views

app_name = 'aahaara_care'

urlpatterns = [
    # Chat dashboard and sessions
    path('', views.chat_dashboard, name='chat_dashboard'),
    path('chat/<uuid:session_id>/', views.chat_session, name='chat_session'),
    path('chat/<uuid:session_id>/send/', views.send_message, name='send_message'),
    path('new-session/', views.create_new_session, name='create_new_session'),
    path('sessions/', views.session_list, name='session_list'),
    
    # Feedback
    path('feedback/<uuid:message_id>/', views.submit_feedback, name='submit_feedback'),
    
    # Message management
    path('message/<uuid:message_id>/edit/', views.edit_message, name='edit_message'),
    path('message/<uuid:message_id>/delete/', views.delete_message, name='delete_message'),
    path('session/<uuid:session_id>/delete/', views.delete_session, name='delete_session'),
    path('messages/bulk-delete/', views.bulk_delete_messages, name='bulk_delete_messages'),
    
    # Knowledge base
    path('knowledge/', views.knowledge_base, name='knowledge_base'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]
