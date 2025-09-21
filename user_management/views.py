from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import json
import logging

from .models import (
    UserProfile, PatientProfile, DietitianProfile, Appointment,
    PrakritiQuestion, PrakritiOption, PrakritiResponse,
    DiseaseQuestion, DiseaseResponse
)
from .forms import (
    UserRegistrationForm, PatientProfileForm, DietitianProfileForm,
    AppointmentForm, VirtualMeetingForm
)

logger = logging.getLogger(__name__)


def home(request):
    """Main entry point - show landing page or redirect to dashboard"""
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return redirect('user_management:dashboard')
        except UserProfile.DoesNotExist:
            return redirect('user_management:register')
    else:
        return render(request, 'user_management/home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            return redirect('user_management:complete_profile')
    else:
        # Pre-select user type if provided in URL
        initial_data = {}
        user_type = request.GET.get('type')
        if user_type in ['patient', 'dietitian']:
            initial_data['user_type'] = user_type
        form = UserRegistrationForm(initial=initial_data)
    
    return render(request, 'user_management/register.html', {'form': form})


@login_required
def complete_profile(request):
    """Complete user profile after registration"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type == 'patient':
        profile = get_object_or_404(PatientProfile, user_profile=user_profile)
        form_class = PatientProfileForm
        template = 'user_management/complete_patient_profile.html'
    else:
        profile = get_object_or_404(DietitianProfile, user_profile=user_profile)
        form_class = DietitianProfileForm
        template = 'user_management/complete_dietitian_profile.html'
    
    if request.method == 'POST':
        form = form_class(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile completed successfully!')
            return redirect('user_management:dashboard')
    else:
        form = form_class(instance=profile)
    
    return render(request, template, {'form': form, 'user_profile': user_profile})


@login_required
def dashboard(request):
    """User dashboard based on user type"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # If no profile exists, redirect to registration
        messages.info(request, 'Please complete your registration first.')
        return redirect('user_management:register')
    
    if user_profile.user_type == 'patient':
        return patient_dashboard(request)
    else:
        return dietitian_dashboard(request)


def patient_dashboard(request):
    """Patient dashboard"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    patient_profile = get_object_or_404(PatientProfile, user_profile=user_profile)
    
    # Get recent appointments
    recent_appointments = Appointment.objects.filter(
        patient=user_profile
    ).order_by('-appointment_date')[:5]
    
    # Get diet charts (if any) - using the new relationship
    from diet_planner.models import DietChart
    try:
        diet_patient = user_profile.diet_patient
        diet_charts = DietChart.objects.filter(patient=diet_patient).order_by('-created_at')[:5]
    except:
        diet_charts = []
    
    context = {
        'user_profile': user_profile,
        'patient_profile': patient_profile,
        'recent_appointments': recent_appointments,
        'diet_charts': diet_charts,
    }
    
    return render(request, 'user_management/patient_dashboard.html', context)


def dietitian_dashboard(request):
    """Dietitian dashboard"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    dietitian_profile = get_object_or_404(DietitianProfile, user_profile=user_profile)
    
    # Get today's appointments
    from django.utils import timezone
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        dietitian=user_profile,
        appointment_date__date=today
    ).order_by('appointment_date')
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        dietitian=user_profile,
        appointment_date__date__gt=today
    ).order_by('appointment_date')[:10]
    
    # Get all patients
    patients = UserProfile.objects.filter(user_type='patient').order_by('-created_at')[:10]
    
    context = {
        'user_profile': user_profile,
        'dietitian_profile': dietitian_profile,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'patients': patients,
    }
    
    return render(request, 'user_management/dietitian_dashboard.html', context)


@login_required
def book_appointment(request):
    """Book appointment with dietitian"""
    # Get all registered dietitians
    dietitians = UserProfile.objects.filter(user_type='dietitian').order_by('user__first_name')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Create appointment manually since it's a regular Form, not ModelForm
            appointment = Appointment.objects.create(
                patient=get_object_or_404(UserProfile, user=request.user),
                dietitian=form.cleaned_data['dietitian'],
                appointment_date=form.cleaned_data['appointment_date'],
                appointment_type=form.cleaned_data['appointment_type'],
                reason_for_visit=form.cleaned_data['reason_for_visit'],
                duration_minutes=form.cleaned_data['duration_minutes'],
                consultation_fee=form.cleaned_data['consultation_fee'],
                status='scheduled'
            )
            messages.success(request, 'Appointment booked successfully!')
            return redirect('user_management:dashboard')
    else:
        form = AppointmentForm()
    
    context = {
        'form': form,
        'dietitians': dietitians,
    }
    
    return render(request, 'user_management/book_appointment.html', context)


@login_required
def appointment_list(request):
    """List user's appointments"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type == 'patient':
        appointments = Appointment.objects.filter(patient=user_profile)
    else:
        appointments = Appointment.objects.filter(dietitian=user_profile)
    
    appointments = appointments.order_by('-appointment_date')
    
    # Pagination
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    appointments = paginator.get_page(page_number)
    
    context = {
        'appointments': appointments,
        'user_profile': user_profile,
    }
    
    return render(request, 'user_management/appointment_list.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """Appointment detail view"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has access to this appointment
    if user_profile.user_type == 'patient':
        if appointment.patient != user_profile:
            messages.error(request, 'You do not have access to this appointment.')
            return redirect('user_management:dashboard')
    else:
        if appointment.dietitian != user_profile:
            messages.error(request, 'You do not have access to this appointment.')
            return redirect('user_management:dashboard')
    
    context = {
        'appointment': appointment,
        'user_profile': user_profile,
    }
    
    return render(request, 'user_management/appointment_detail.html', context)


@login_required
def prakriti_analysis(request, patient_id=None):
    """Prakriti analysis test - for dietitians to conduct on specific patients"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'dietitian':
        messages.error(request, 'Only dietitians can conduct the Prakriti analysis.')
        return redirect('user_management:dashboard')
    
    # Get patient ID from URL parameter or form
    patient_id = patient_id or request.GET.get('patient_id') or request.POST.get('patient_id')
    
    if not patient_id:
        # Show patient selection page
        patients = UserProfile.objects.filter(user_type='patient').order_by('-created_at')
        context = {
            'user_profile': user_profile,
            'patients': patients,
            'show_patient_selection': True,
        }
        return render(request, 'user_management/prakriti_analysis.html', context)
    
    # Get the specific patient
    patient_profile = get_object_or_404(UserProfile, id=patient_id, user_type='patient')
    
    # Get questions
    questions = PrakritiQuestion.objects.filter(is_active=True).order_by('question_number')
    
    if request.method == 'POST':
        # Process responses
        responses = []
        for question in questions:
            option_id = request.POST.get(f'question_{question.id}')
            if option_id:
                try:
                    option = PrakritiOption.objects.get(id=option_id)
                    response, created = PrakritiResponse.objects.get_or_create(
                        patient=patient_profile,
                        question=question,
                        defaults={'selected_option': option}
                    )
                    if not created:
                        response.selected_option = option
                        response.save()
                    responses.append(response)
                except PrakritiOption.DoesNotExist:
                    pass
        
        if len(responses) == questions.count():
            # Calculate Prakriti scores
            vata_score = sum(r.selected_option.weight for r in responses if r.selected_option.dosha_type == 'vata')
            pitta_score = sum(r.selected_option.weight for r in responses if r.selected_option.dosha_type == 'pitta')
            kapha_score = sum(r.selected_option.weight for r in responses if r.selected_option.dosha_type == 'kapha')
            
            total_score = vata_score + pitta_score + kapha_score
            
            # Calculate percentages
            vata_percentage = (vata_score / total_score) * 100 if total_score > 0 else 0
            pitta_percentage = (pitta_score / total_score) * 100 if total_score > 0 else 0
            kapha_percentage = (kapha_score / total_score) * 100 if total_score > 0 else 0
            
            # Determine dominant dosha
            dosha_scores = {
                'vata': vata_percentage,
                'pitta': pitta_percentage,
                'kapha': kapha_percentage
            }
            dominant_dosha = max(dosha_scores, key=dosha_scores.get)
            
            # Update patient profile
            patient_profile_obj = get_object_or_404(PatientProfile, user_profile=patient_profile)
            patient_profile_obj.vata_percentage = vata_percentage
            patient_profile_obj.pitta_percentage = pitta_percentage
            patient_profile_obj.kapha_percentage = kapha_percentage
            patient_profile_obj.dominant_dosha = dominant_dosha
            patient_profile_obj.prakriti_analysis_completed = True
            
            # Assign patient to the doctor conducting the analysis
            current_user_profile = get_object_or_404(UserProfile, user=request.user)
            if current_user_profile.user_type == 'dietitian':
                patient_profile_obj.assigned_doctor = current_user_profile
            
            patient_profile_obj.save()
            
            messages.success(request, f'Prakriti analysis completed successfully for {patient_profile.user.get_full_name()}!')
            return redirect('user_management:disease_analysis_patient', patient_id=patient_id)
    
    context = {
        'questions': questions,
        'user_profile': user_profile,
        'patient_profile': patient_profile,
        'show_patient_selection': False,
    }
    
    return render(request, 'user_management/prakriti_analysis.html', context)


@login_required
def disease_analysis(request, patient_id=None):
    """Disease analysis test - for dietitians to conduct on specific patients"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'dietitian':
        messages.error(request, 'Only dietitians can conduct the disease analysis.')
        return redirect('user_management:dashboard')
    
    # Get patient ID from URL parameter or form
    patient_id = patient_id or request.GET.get('patient_id') or request.POST.get('patient_id')
    
    if not patient_id:
        # Show patient selection page
        patients = UserProfile.objects.filter(user_type='patient').order_by('-created_at')
        context = {
            'user_profile': user_profile,
            'patients': patients,
            'show_patient_selection': True,
        }
        return render(request, 'user_management/disease_analysis.html', context)
    
    # Get the specific patient
    patient_profile = get_object_or_404(UserProfile, id=patient_id, user_type='patient')
    
    # Get questions
    questions = DiseaseQuestion.objects.filter(is_active=True).order_by('question_number')
    
    if request.method == 'POST':
        # Process responses
        for question in questions:
            response_value = request.POST.get(f'question_{question.id}')
            notes = request.POST.get(f'notes_{question.id}', '')
            
            if response_value:
                response, created = DiseaseResponse.objects.get_or_create(
                    patient=patient_profile,
                    question=question,
                    defaults={'response': response_value, 'notes': notes}
                )
                if not created:
                    response.response = response_value
                    response.notes = notes
                    response.save()
        
        # Mark disease analysis as completed
        patient_profile_obj = get_object_or_404(PatientProfile, user_profile=patient_profile)
        patient_profile_obj.disease_analysis_completed = True
        patient_profile_obj.save()
        
        messages.success(request, f'Disease analysis completed successfully for {patient_profile.user.get_full_name()}!')
        return redirect('user_management:health_summary_patient', patient_id=patient_id)
    
    context = {
        'questions': questions,
        'user_profile': user_profile,
        'patient_profile': patient_profile,
        'show_patient_selection': False,
    }
    
    return render(request, 'user_management/disease_analysis.html', context)


@login_required
def health_summary(request, patient_id=None):
    """Health summary with calorie recommendations - for dietitians to generate for specific patients"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'dietitian':
        messages.error(request, 'Only dietitians can generate health summaries.')
        return redirect('user_management:dashboard')
    
    # Get patient ID from URL parameter or form
    patient_id = patient_id or request.GET.get('patient_id') or request.POST.get('patient_id')
    
    if not patient_id:
        # Show patient selection page
        patients = UserProfile.objects.filter(user_type='patient').order_by('-created_at')
        context = {
            'user_profile': user_profile,
            'patients': patients,
            'show_patient_selection': True,
        }
        return render(request, 'user_management/health_summary.html', context)
    
    # Get the specific patient
    patient_profile = get_object_or_404(UserProfile, id=patient_id, user_type='patient')
    patient_profile_obj = get_object_or_404(PatientProfile, user_profile=patient_profile)
    
    # Calculate calorie needs if not already calculated
    if not patient_profile_obj.health_summary_generated:
        calculate_calorie_needs(patient_profile_obj)
    
    context = {
        'user_profile': user_profile,
        'patient_profile': patient_profile_obj,
        'selected_patient': patient_profile,
        'show_patient_selection': False,
    }
    
    return render(request, 'user_management/health_summary.html', context)


def calculate_calorie_needs(patient_profile):
    """Calculate daily calorie needs based on patient profile"""
    # Check if required data is available
    if not patient_profile.weight or not patient_profile.height:
        # Use default values if data is missing
        weight = patient_profile.weight or 70.0  # Default 70kg
        height = patient_profile.height or 170.0  # Default 170cm
        age = 30  # Default age
    else:
        weight = patient_profile.weight
        height = patient_profile.height
        age = 30  # Default age
    
    # Harris-Benedict formula for BMR calculation
    if patient_profile.gender == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    # Activity factor (assuming moderate activity)
    activity_factor = 1.55
    daily_calories = bmr * activity_factor
    
    # Meal distribution
    breakfast_calories = daily_calories * 0.25  # 25%
    lunch_calories = daily_calories * 0.35      # 35%
    dinner_calories = daily_calories * 0.25     # 25%
    snack_calories = daily_calories * 0.15      # 15%
    
    # Update patient profile
    patient_profile.daily_calorie_needs = daily_calories
    patient_profile.breakfast_calories = breakfast_calories
    patient_profile.lunch_calories = lunch_calories
    patient_profile.dinner_calories = dinner_calories
    patient_profile.snack_calories = snack_calories
    patient_profile.health_summary_generated = True
    patient_profile.save()


@login_required
def virtual_meeting(request, appointment_id):
    """Virtual meeting interface"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user has access to this appointment
    if user_profile.user_type == 'patient':
        if appointment.patient != user_profile:
            messages.error(request, 'You do not have access to this meeting.')
            return redirect('user_management:dashboard')
    else:
        if appointment.dietitian != user_profile:
            messages.error(request, 'You do not have access to this meeting.')
            return redirect('user_management:dashboard')
    
    if request.method == 'POST':
        form = VirtualMeetingForm(request.POST)
        if form.is_valid():
            appointment.meeting_link = form.cleaned_data['meeting_link']
            appointment.meeting_id = form.cleaned_data['meeting_id']
            appointment.meeting_password = form.cleaned_data['meeting_password']
            appointment.save()
            messages.success(request, 'Meeting details updated successfully!')
            return redirect('user_management:appointment_detail', appointment_id=appointment_id)
    else:
        form = VirtualMeetingForm(initial={
            'meeting_link': appointment.meeting_link,
            'meeting_id': appointment.meeting_id,
            'meeting_password': appointment.meeting_password,
        })
    
    context = {
        'appointment': appointment,
        'form': form,
        'user_profile': user_profile,
    }
    
    return render(request, 'user_management/virtual_meeting.html', context)


def custom_logout(request):
    """Custom logout view with options"""
    logout(request)
    return render(request, 'user_management/logout.html')


def logout_options(request):
    """Show logout options page"""
    return render(request, 'user_management/logout_options.html')


def custom_login(request):
    """Custom login view with proper redirect handling"""
    if request.user.is_authenticated:
        return redirect('user_management:dashboard')
    
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Check if user has a profile
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    return redirect('user_management:dashboard')
                except UserProfile.DoesNotExist:
                    # If no profile exists, redirect to registration
                    messages.info(request, 'Please complete your profile first.')
                    return redirect('user_management:register')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'user_management/login.html')