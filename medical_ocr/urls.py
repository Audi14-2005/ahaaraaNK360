from django.urls import path
from . import views

urlpatterns = [
    # Main views
    path('', views.dashboard, name='medical_dashboard'),
    path('upload/', views.upload_document, name='upload_document'),
    path('documents/', views.document_list, name='document_list'),
    path('document/<uuid:document_id>/', views.document_detail, name='document_detail'),
    path('profile/', views.doctor_profile, name='doctor_profile'),
    path('analytics/', views.analytics, name='analytics'),
    
    # API endpoints
    path('api/document/<uuid:document_id>/status/', views.api_document_status, name='api_document_status'),
    path('api/document/<uuid:document_id>/summary/', views.api_document_summary, name='api_document_summary'),
    
    # Actions
    path('document/<uuid:document_id>/reprocess/', views.reprocess_document, name='reprocess_document'),
    path('document/<uuid:document_id>/edit/', views.edit_document, name='edit_document'),
    path('document/<uuid:document_id>/delete/', views.delete_document, name='delete_document'),
    path('documents/bulk-delete/', views.bulk_delete_documents, name='bulk_delete_documents'),
]
