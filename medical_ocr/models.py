from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import uuid


class MedicalDocument(models.Model):
    DOCUMENT_TYPES = [
        ('prescription', 'Prescription'),
        ('lab_report', 'Lab Report'),
        ('radiology', 'Radiology Report'),
        ('discharge_summary', 'Discharge Summary'),
        ('consultation', 'Consultation Note'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_documents')
    patient_name = models.CharField(max_length=200)
    patient_id = models.CharField(max_length=100, blank=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    original_file = models.FileField(
        upload_to='medical_documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'png', 'jpg', 'jpeg', 'tiff'])]
    )
    extracted_text = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    key_findings = models.JSONField(default=list, blank=True)
    medications = models.JSONField(default=list, blank=True)
    vital_signs = models.JSONField(default=dict, blank=True)
    diagnosis = models.JSONField(default=list, blank=True)
    recommendations = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient_name} - {self.get_document_type_display()}"


class DocumentAnalysis(models.Model):
    document = models.OneToOneField(MedicalDocument, on_delete=models.CASCADE, related_name='analysis')
    raw_ocr_text = models.TextField()
    structured_data = models.JSONField(default=dict)
    medical_entities = models.JSONField(default=list)
    risk_factors = models.JSONField(default=list)
    follow_up_required = models.BooleanField(default=False)
    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='low'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis for {self.document.patient_name}"


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    medical_license = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    hospital_affiliation = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"
