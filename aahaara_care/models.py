from django.db import models
from django.contrib.auth.models import User
import uuid


class ChatSession(models.Model):
    """Represents a chat session between a doctor and AAHAARA Care"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat Session - {self.doctor.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    """Represents individual messages in a chat session"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('assistant', 'AAHAARA Care Response'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Medical context
    medical_context = models.JSONField(default=dict, blank=True)
    confidence_score = models.FloatField(default=0.0)
    is_medical_advice = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_message_type_display()} - {self.timestamp.strftime('%H:%M')}"


class MedicalKnowledgeBase(models.Model):
    """Knowledge base for medical information and guidelines"""
    CATEGORIES = [
        ('symptoms', 'Symptoms'),
        ('diagnosis', 'Diagnosis'),
        ('treatment', 'Treatment'),
        ('medication', 'Medication'),
        ('procedures', 'Procedures'),
        ('guidelines', 'Guidelines'),
        ('emergency', 'Emergency'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    keywords = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"


class ChatFeedback(models.Model):
    """Feedback from doctors about AAHAARA Care responses"""
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='feedback')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback_text = models.TextField(blank=True)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback - {self.doctor.username} - Rating: {self.rating}"
