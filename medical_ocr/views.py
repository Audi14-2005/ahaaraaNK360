from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import threading
from .models import MedicalDocument, DocumentAnalysis, DoctorProfile
from .forms import MedicalDocumentForm, DoctorProfileForm, DocumentSearchForm
from .services import MedicalDocumentProcessor
from .tasks import process_document_async


@login_required
def dashboard(request):
    """Doctor dashboard showing recent documents and summaries"""
    # Get recent documents
    recent_documents = MedicalDocument.objects.filter(doctor=request.user)[:5]
    
    # Get statistics
    total_documents = MedicalDocument.objects.filter(doctor=request.user).count()
    completed_documents = MedicalDocument.objects.filter(
        doctor=request.user, 
        processing_status='completed'
    ).count()
    pending_documents = MedicalDocument.objects.filter(
        doctor=request.user, 
        processing_status='processing'
    ).count()
    
    # Get high priority documents
    high_priority = MedicalDocument.objects.filter(
        doctor=request.user,
        analysis__urgency_level__in=['high', 'critical']
    )[:3]
    
    context = {
        'recent_documents': recent_documents,
        'total_documents': total_documents,
        'completed_documents': completed_documents,
        'pending_documents': pending_documents,
        'high_priority': high_priority,
    }
    return render(request, 'medical_ocr/dashboard.html', context)


@login_required
def upload_document(request):
    """Upload and process medical documents"""
    if request.method == 'POST':
        form = MedicalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.doctor = request.user
            document.save()
            
            # Process document synchronously (no Redis needed)
            try:
                from .tasks import process_document_async
                process_document_async(document.id)
            except Exception as e:
                # Fallback: process directly without async
                try:
                    from .services import MedicalDocumentProcessor
                    processor = MedicalDocumentProcessor()
                    result = processor.process_document(document.original_file.path, document.document_type)
                    
                    if result['success']:
                        document.extracted_text = result['extracted_text']
                        document.ai_summary = result['ai_summary']
                        document.medications = result['medications']
                        document.vital_signs = result['vital_signs']
                        document.diagnosis = result['diagnosis']
                        document.key_findings = result['key_findings']
                        document.confidence_score = result['confidence_score']
                        document.processing_status = 'completed'
                        document.save()
                        messages.success(request, 'Document processed successfully!')
                    else:
                        document.processing_status = 'failed'
                        document.error_message = result.get('error', 'Unknown error')
                        document.save()
                        messages.error(request, f'Document processing failed: {result.get("error", "Unknown error")}')
                except Exception as processing_error:
                    document.processing_status = 'failed'
                    document.error_message = str(processing_error)
                    document.save()
                    messages.error(request, f'Document processing failed: {str(processing_error)}')
            
            messages.success(request, 'Document uploaded successfully! Processing will begin shortly.')
            return redirect('document_detail', document_id=document.id)
    else:
        form = MedicalDocumentForm()
    
    return render(request, 'medical_ocr/upload_document.html', {'form': form})


@login_required
def document_list(request):
    """List all documents with search and filter"""
    search_form = DocumentSearchForm(request.GET)
    documents = MedicalDocument.objects.filter(doctor=request.user)
    
    if search_form.is_valid():
        if search_form.cleaned_data.get('patient_name'):
            documents = documents.filter(
                patient_name__icontains=search_form.cleaned_data['patient_name']
            )
        if search_form.cleaned_data.get('document_type'):
            documents = documents.filter(
                document_type=search_form.cleaned_data['document_type']
            )
        if search_form.cleaned_data.get('date_from'):
            documents = documents.filter(
                created_at__date__gte=search_form.cleaned_data['date_from']
            )
        if search_form.cleaned_data.get('date_to'):
            documents = documents.filter(
                created_at__date__lte=search_form.cleaned_data['date_to']
            )
    
    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'medical_ocr/document_list.html', context)


@login_required
def document_detail(request, document_id):
    """View detailed analysis of a medical document"""
    document = get_object_or_404(MedicalDocument, id=document_id, doctor=request.user)
    
    try:
        analysis = document.analysis
    except DocumentAnalysis.DoesNotExist:
        analysis = None
    
    context = {
        'document': document,
        'analysis': analysis,
    }
    return render(request, 'medical_ocr/document_detail.html', context)


@login_required
def doctor_profile(request):
    """Manage doctor profile"""
    try:
        profile = request.user.doctorprofile
    except DoctorProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('doctor_profile')
    else:
        form = DoctorProfileForm(instance=profile)
    
    return render(request, 'medical_ocr/doctor_profile.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def reprocess_document(request, document_id):
    """Reprocess a document"""
    document = get_object_or_404(MedicalDocument, id=document_id, doctor=request.user)
    
    # Reset processing status
    document.processing_status = 'uploaded'
    document.save()
    
    # Process document synchronously (no Redis needed)
    try:
        from .tasks import process_document_async
        process_document_async(document.id)
    except Exception as e:
        # Fallback: process directly without async
        try:
            from .services import MedicalDocumentProcessor
            processor = MedicalDocumentProcessor()
            result = processor.process_document(document.original_file.path, document.document_type)
            
            if result['success']:
                document.extracted_text = result['extracted_text']
                document.ai_summary = result['ai_summary']
                document.medications = result['medications']
                document.vital_signs = result['vital_signs']
                document.diagnosis = result['diagnosis']
                document.key_findings = result['key_findings']
                document.confidence_score = result['confidence_score']
                document.processing_status = 'completed'
                document.error_message = ''  # Clear any previous error
                document.save()
                messages.success(request, 'Document reprocessed successfully!')
            else:
                document.processing_status = 'failed'
                document.error_message = result.get('error', 'Unknown error')
                document.save()
                messages.error(request, f'Document reprocessing failed: {result.get("error", "Unknown error")}')
        except Exception as processing_error:
            document.processing_status = 'failed'
            document.error_message = str(processing_error)
            document.save()
            messages.error(request, f'Document reprocessing failed: {str(processing_error)}')
    
    messages.success(request, 'Document reprocessing started!')
    return redirect('document_detail', document_id=document.id)


@login_required
def api_document_status(request, document_id):
    """API endpoint to check document processing status"""
    document = get_object_or_404(MedicalDocument, id=document_id, doctor=request.user)
    
    return JsonResponse({
        'status': document.processing_status,
        'confidence_score': document.confidence_score,
        'has_analysis': hasattr(document, 'analysis')
    })


@login_required
def api_document_summary(request, document_id):
    """API endpoint to get document summary"""
    document = get_object_or_404(MedicalDocument, id=document_id, doctor=request.user)
    
    if document.processing_status != 'completed':
        return JsonResponse({'error': 'Document not processed yet'}, status=400)
    
    return JsonResponse({
        'summary': document.ai_summary,
        'medications': document.medications,
        'vital_signs': document.vital_signs,
        'diagnosis': document.diagnosis,
        'key_findings': document.key_findings,
        'confidence_score': document.confidence_score
    })


@login_required
def analytics(request):
    """Analytics dashboard for doctors"""
    # Get document statistics
    documents = MedicalDocument.objects.filter(doctor=request.user)
    
    # Document type distribution
    doc_type_stats = {}
    for doc_type, _ in MedicalDocument.DOCUMENT_TYPES:
        count = documents.filter(document_type=doc_type).count()
        if count > 0:
            doc_type_stats[doc_type] = count
    
    # Processing status distribution
    status_stats = {}
    for status, _ in MedicalDocument.STATUS_CHOICES:
        count = documents.filter(processing_status=status).count()
        if count > 0:
            status_stats[status] = count
    
    # Monthly document count
    monthly_stats = {}
    for doc in documents:
        month_key = doc.created_at.strftime('%Y-%m')
        monthly_stats[month_key] = monthly_stats.get(month_key, 0) + 1
    
    context = {
        'doc_type_stats': doc_type_stats,
        'status_stats': status_stats,
        'monthly_stats': monthly_stats,
        'total_documents': documents.count(),
    }
    return render(request, 'medical_ocr/analytics.html', context)


@login_required
def edit_document(request, document_id):
    """Edit a medical document"""
    document = get_object_or_404(MedicalDocument, id=document_id, doctor=request.user)
    
    if request.method == 'POST':
        form = MedicalDocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            # Save the form
            updated_document = form.save(commit=False)
            updated_document.doctor = request.user
            
            # If a new file was uploaded, reprocess the document
            if 'original_file' in request.FILES:
                updated_document.processing_status = 'uploaded'
                updated_document.ai_summary = ''
                updated_document.medications = ''
                updated_document.vital_signs = ''
                updated_document.diagnosis = ''
                updated_document.key_findings = ''
                updated_document.confidence_score = 0.0
                updated_document.error_message = ''
            
            updated_document.save()
            
            # Reprocess if new file was uploaded
            if 'original_file' in request.FILES:
                try:
                    from .services import MedicalDocumentProcessor
                    processor = MedicalDocumentProcessor()
                    result = processor.process_document(updated_document.original_file.path, updated_document.document_type)

                    if result['success']:
                        updated_document.extracted_text = result['extracted_text']
                        updated_document.ai_summary = result['ai_summary']
                        updated_document.medications = result['medications']
                        updated_document.vital_signs = result['vital_signs']
                        updated_document.diagnosis = result['diagnosis']
                        updated_document.key_findings = result['key_findings']
                        updated_document.confidence_score = result['confidence_score']
                        updated_document.processing_status = 'completed'
                        updated_document.save()
                        messages.success(request, 'Document updated and reprocessed successfully!')
                    else:
                        updated_document.processing_status = 'failed'
                        updated_document.error_message = result.get('error', 'Unknown error')
                        updated_document.save()
                        messages.error(request, f'Document processing failed: {result.get("error", "Unknown error")}')
                except Exception as processing_error:
                    updated_document.processing_status = 'failed'
                    updated_document.error_message = str(processing_error)
                    updated_document.save()
                    messages.error(request, f'Document processing failed: {str(processing_error)}')
            else:
                messages.success(request, 'Document updated successfully!')
            
            return redirect('document_detail', document_id=updated_document.id)
    else:
        form = MedicalDocumentForm(instance=document)
    
    context = {
        'form': form,
        'document': document,
        'title': 'Edit Document'
    }
    return render(request, 'medical_ocr/edit_document.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def delete_document(request, document_id):
    """Delete a medical document"""
    try:
        document = get_object_or_404(MedicalDocument, id=document_id, doctor=request.user)
        
        # Delete the file if it exists
        if document.original_file:
            try:
                document.original_file.delete(save=False)
            except:
                pass  # File might not exist
        
        # Delete the document record
        document.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Document deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def bulk_delete_documents(request):
    """Delete multiple medical documents"""
    try:
        data = json.loads(request.body)
        document_ids = data.get('document_ids', [])
        
        if not document_ids:
            return JsonResponse({
                'success': False,
                'error': 'No documents selected'
            }, status=400)
        
        # Get documents that belong to the user
        documents = MedicalDocument.objects.filter(
            id__in=document_ids,
            doctor=request.user
        )
        
        deleted_count = 0
        for document in documents:
            # Delete the file if it exists
            if document.original_file:
                try:
                    document.original_file.delete(save=False)
                except:
                    pass  # File might not exist
            
            # Delete the document record
            document.delete()
            deleted_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} documents deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
