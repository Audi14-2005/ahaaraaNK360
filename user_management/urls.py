from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    # Main entry point - redirect to appropriate page
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('dietitian-dashboard/', views.dietitian_dashboard, name='dietitian_dashboard'),
    
    # Appointments
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<uuid:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<uuid:appointment_id>/virtual-meeting/', views.virtual_meeting, name='virtual_meeting'),
    
    # Analysis Tests
    path('prakriti-analysis/', views.prakriti_analysis, name='prakriti_analysis'),
    path('prakriti-analysis/<uuid:patient_id>/', views.prakriti_analysis, name='prakriti_analysis_patient'),
    path('disease-analysis/', views.disease_analysis, name='disease_analysis'),
    path('disease-analysis/<uuid:patient_id>/', views.disease_analysis, name='disease_analysis_patient'),
    path('health-summary/', views.health_summary, name='health_summary'),
    path('health-summary/<uuid:patient_id>/', views.health_summary, name='health_summary_patient'),
    
    # Authentication
    path('login/', views.custom_login, name='custom_login'),
    
    # Logout
    path('logout/', views.custom_logout, name='custom_logout'),
    path('logout-options/', views.logout_options, name='logout_options'),
]
