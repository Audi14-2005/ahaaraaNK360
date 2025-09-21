from django.contrib import admin
from .models import MedicalDocument, DocumentAnalysis, DoctorProfile


@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'document_type', 'doctor', 'processing_status', 'created_at']
    list_filter = ['document_type', 'processing_status', 'created_at', 'doctor']
    search_fields = ['patient_name', 'patient_id', 'extracted_text']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'doctor', 'patient_name', 'patient_id', 'document_type')
        }),
        ('Document', {
            'fields': ('original_file', 'processing_status')
        }),
        ('Analysis Results', {
            'fields': ('extracted_text', 'ai_summary', 'key_findings', 'medications', 
                      'vital_signs', 'diagnosis', 'recommendations', 'confidence_score')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DocumentAnalysis)
class DocumentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['document', 'urgency_level', 'follow_up_required', 'created_at']
    list_filter = ['urgency_level', 'follow_up_required', 'created_at']
    readonly_fields = ['created_at']


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'hospital_affiliation']
    search_fields = ['user__username', 'user__email', 'medical_license']


