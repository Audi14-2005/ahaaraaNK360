try:
    from celery import shared_task
except ImportError:
    # Fallback for when Celery is not available
    def shared_task(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
from django.conf import settings
import os
import logging
from .models import MedicalDocument, DocumentAnalysis
from .services import MedicalDocumentProcessor

logger = logging.getLogger(__name__)


@shared_task
def process_document_async(document_id):
    """Asynchronously process a medical document"""
    try:
        document = MedicalDocument.objects.get(id=document_id)
        document.processing_status = 'processing'
        document.save()
        
        # Get document path
        document_path = document.original_file.path
        
        # Process document
        processor = MedicalDocumentProcessor()
        result = processor.process_document(document_path, document.document_type)
        
        if result['success']:
            # Update document with results
            document.extracted_text = result['extracted_text']
            document.ai_summary = result['ai_summary']
            document.medications = result['medications']
            document.vital_signs = result['vital_signs']
            document.diagnosis = result['diagnosis']
            document.key_findings = result['key_findings']
            document.confidence_score = result['confidence_score']
            document.processing_status = 'completed'
            document.save()
            
            # Create analysis record
            analysis, created = DocumentAnalysis.objects.get_or_create(
                document=document,
                defaults={
                    'raw_ocr_text': result['extracted_text'],
                    'structured_data': {
                        'medications': result['medications'],
                        'vital_signs': result['vital_signs'],
                        'diagnosis': result['diagnosis'],
                        'key_findings': result['key_findings']
                    },
                    'medical_entities': result.get('medical_entities', []),
                    'risk_factors': result.get('risk_factors', []),
                    'follow_up_required': _determine_follow_up(result),
                    'urgency_level': _determine_urgency(result)
                }
            )
            
            logger.info(f"Successfully processed document {document_id}")
            
        else:
            document.processing_status = 'failed'
            document.save()
            logger.error(f"Failed to process document {document_id}: {result.get('error', 'Unknown error')}")
            
    except MedicalDocument.DoesNotExist:
        logger.error(f"Document {document_id} not found")
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        try:
            document = MedicalDocument.objects.get(id=document_id)
            document.processing_status = 'failed'
            document.save()
        except:
            pass


def _determine_follow_up(result):
    """Determine if follow-up is required based on analysis results"""
    # Check for high-risk keywords or conditions
    high_risk_keywords = [
        'urgent', 'emergency', 'critical', 'severe', 'abnormal',
        'elevated', 'decreased', 'positive', 'negative'
    ]
    
    text = result.get('extracted_text', '').lower()
    summary = result.get('ai_summary', '').lower()
    
    for keyword in high_risk_keywords:
        if keyword in text or keyword in summary:
            return True
    
    return False


def _determine_urgency(result):
    """Determine urgency level based on analysis results"""
    critical_keywords = ['critical', 'emergency', 'urgent', 'severe']
    high_keywords = ['abnormal', 'elevated', 'decreased', 'positive']
    
    text = result.get('extracted_text', '').lower()
    summary = result.get('ai_summary', '').lower()
    combined_text = text + ' ' + summary
    
    for keyword in critical_keywords:
        if keyword in combined_text:
            return 'critical'
    
    for keyword in high_keywords:
        if keyword in combined_text:
            return 'high'
    
    # Check if vital signs are present (indicates medical document)
    if result.get('vital_signs') or result.get('medications'):
        return 'medium'
    
    return 'low'
