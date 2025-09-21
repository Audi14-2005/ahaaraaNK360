from django.contrib import admin
from .models import ChatSession, ChatMessage, MedicalKnowledgeBase, ChatFeedback


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'title', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'doctor']
    search_fields = ['title', 'doctor__username', 'doctor__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'message_type', 'timestamp', 'confidence_score', 'is_medical_advice']
    list_filter = ['message_type', 'is_medical_advice', 'timestamp', 'session__doctor']
    search_fields = ['content', 'session__title', 'session__doctor__username']
    readonly_fields = ['id', 'timestamp']
    ordering = ['-timestamp']


@admin.register(MedicalKnowledgeBase)
class MedicalKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'created_at', 'updated_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'keywords']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['category', 'title']


@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'message', 'rating', 'is_helpful', 'created_at']
    list_filter = ['rating', 'is_helpful', 'created_at', 'doctor']
    search_fields = ['feedback_text', 'doctor__username', 'message__content']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
