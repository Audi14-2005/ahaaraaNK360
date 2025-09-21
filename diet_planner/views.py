from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import json
import logging
from .models import Patient, Food, DietChart, MealPlan, MealItem, FoodSwapLog, Recipe
from .services import DietArchitectAI, FoodSpecialistAI, RecipeGeneratorAI
from .forms import PatientForm, PatientBasicInfoForm

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Main dashboard for diet planning system - different views for patients vs dietitians"""
    from user_management.models import UserProfile
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.user_type == 'patient':
            # Patient view - show only their diet charts
            try:
                # Find the Patient instance linked to this user_profile
                diet_patient = Patient.objects.get(user_profile=user_profile)
                # Get diet charts for this patient
                diet_charts = DietChart.objects.filter(patient=diet_patient).order_by('-created_at')
                
                context = {
                    'user_profile': user_profile,
                    'diet_charts': diet_charts,
                    'is_patient': True,
                }
                return render(request, 'diet_planner/patient_dashboard.html', context)
                
            except Patient.DoesNotExist:
                # If no diet_patient exists, show empty state
                context = {
                    'user_profile': user_profile,
                    'diet_charts': [],
                    'is_patient': True,
                }
                return render(request, 'diet_planner/patient_dashboard.html', context)
            except Exception as e:
                # If no diet_patient exists, show empty state
                context = {
                    'user_profile': user_profile,
                    'diet_charts': [],
                    'is_patient': True,
                }
                return render(request, 'diet_planner/patient_dashboard.html', context)
        
        else:
            # Dietitian view - show full dashboard
            from user_management.models import PatientProfile
            
            # Get user's assigned patients from user management system
            assigned_patients = UserProfile.objects.filter(
                user_type='patient',
                patient_profile__assigned_doctor=user_profile
            ).order_by('-created_at')
            
            # Get recent diet charts for assigned patients
            recent_charts = DietChart.objects.filter(
                patient__user_profile__patient_profile__assigned_doctor=user_profile
            ).order_by('-created_at')[:5]
            
            # Get statistics
            total_patients = assigned_patients.count()
            total_charts = DietChart.objects.filter(
                patient__user_profile__patient_profile__assigned_doctor=user_profile
            ).count()
            total_foods = Food.objects.filter(is_active=True).count()
    
            # Get charts created this week
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)
            recent_charts_count = DietChart.objects.filter(
                patient__user_profile__patient_profile__assigned_doctor=user_profile,
                created_at__gte=week_ago
            ).count()
            
            context = {
                'patients': assigned_patients,
                'recent_charts': recent_charts,
                'total_patients': total_patients,
                'total_diet_charts': total_charts,
                'total_foods': total_foods,
                'recent_charts_count': recent_charts_count,
                'is_patient': False,
                'user_profile': user_profile,
            }
            return render(request, 'diet_planner/dashboard.html', context)
            
    except UserProfile.DoesNotExist:
        # Fallback for users without profile
        messages.error(request, 'Please complete your profile first.')
        return redirect('user_management:register')


def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None  # Return None instead of string for database field
    from datetime import date
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

@login_required
def patient_list(request):
    """List all patients - only for dietitians"""
    from user_management.models import UserProfile, PatientProfile
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'dietitian':
            messages.error(request, 'Only dietitians can access this page.')
            return redirect('user_management:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('user_management:register')
    
    # Get only patients assigned to the current doctor
    current_user_profile = UserProfile.objects.get(user=request.user)
    patient_users = UserProfile.objects.filter(
        user_type='patient',
        patient_profile__assigned_doctor=current_user_profile
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        patient_users = patient_users.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Get patient profiles for additional info
    patients_with_profiles = []
    for user_profile in patient_users:
        try:
            patient_profile = PatientProfile.objects.get(user_profile=user_profile)
            patients_with_profiles.append({
                'user_profile': user_profile,
                'patient_profile': patient_profile,
                'name': f"{user_profile.user.first_name} {user_profile.user.last_name}".strip() or user_profile.user.username,
                'email': user_profile.user.email,
                'age': calculate_age(patient_profile.user_profile.date_of_birth),
                'gender': patient_profile.gender,
                'medical_conditions': patient_profile.medical_conditions,
                'prakriti_completed': patient_profile.prakriti_analysis_completed,
                'disease_completed': patient_profile.disease_analysis_completed,
                'health_completed': patient_profile.health_summary_generated,
            })
        except PatientProfile.DoesNotExist:
            # Patient without profile
            patients_with_profiles.append({
                'user_profile': user_profile,
                'patient_profile': None,
                'name': f"{user_profile.user.first_name} {user_profile.user.last_name}".strip() or user_profile.user.username,
                'email': user_profile.user.email,
                'age': 'Not set',
                'gender': 'Not set',
                'medical_conditions': 'Not set',
                'prakriti_completed': False,
                'disease_completed': False,
                'health_completed': False,
            })
    
    # Pagination
    paginator = Paginator(patients_with_profiles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'diet_planner/patient_list.html', context)


@login_required
def debug_patient(request, patient_id):
    """Debug view to check patient existence"""
    from user_management.models import UserProfile, PatientProfile
    import uuid
    
    debug_info = {
        'patient_id': patient_id,
        'user': request.user.username,
        'old_system': {},
        'new_system': {},
        'all_patients': [],
        'all_user_profiles': []
    }
    
    try:
        patient_uuid = uuid.UUID(patient_id)
        debug_info['valid_uuid'] = True
    except ValueError:
        debug_info['valid_uuid'] = False
        return JsonResponse(debug_info)
    
    # Check old system
    try:
        patient = Patient.objects.get(id=patient_uuid)
        debug_info['old_system'] = {
            'found': True,
            'name': patient.name,
            'dietitian': patient.dietitian.username,
            'user_profile': str(patient.user_profile) if patient.user_profile else None
        }
    except Patient.DoesNotExist:
        debug_info['old_system'] = {'found': False}
    
    # Check new system
    try:
        user_profile = UserProfile.objects.get(id=patient_uuid, user_type='patient')
        debug_info['new_system'] = {
            'user_profile_found': True,
            'user_name': user_profile.user.get_full_name(),
            'username': user_profile.user.username
        }
        try:
            patient_profile = PatientProfile.objects.get(user_profile=user_profile)
            debug_info['new_system']['patient_profile_found'] = True
            debug_info['new_system']['assigned_doctor'] = str(patient_profile.assigned_doctor) if patient_profile.assigned_doctor else None
        except PatientProfile.DoesNotExist:
            debug_info['new_system']['patient_profile_found'] = False
    except UserProfile.DoesNotExist:
        debug_info['new_system'] = {'user_profile_found': False}
    
    # List all patients for current user
    debug_info['all_patients'] = [
        {'id': str(p.id), 'name': p.name, 'dietitian': p.dietitian.username}
        for p in Patient.objects.filter(dietitian=request.user)
    ]
    
    # List all user profiles
    debug_info['all_user_profiles'] = [
        {'id': str(p.id), 'name': p.user.get_full_name(), 'type': p.user_type}
        for p in UserProfile.objects.filter(user_type='patient')
    ]
    
    return JsonResponse(debug_info, indent=2)


@login_required
def patient_detail(request, patient_id):
    """View patient details and their diet charts"""
    from user_management.models import UserProfile, PatientProfile
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Patient detail request for ID: {patient_id}, User: {request.user.username}")
    
    # First, try to get the patient from the old system (diet_planner.Patient)
    try:
        # Check if patient exists for any dietitian first
        patient_exists = Patient.objects.filter(id=patient_id).exists()
        logger.info(f"Patient exists in old system: {patient_exists}")
        
        if patient_exists:
            # Check if patient belongs to current user
            patient = Patient.objects.get(id=patient_id)
            logger.info(f"Patient found: {patient.name}, Dietitian: {patient.dietitian.username}")
            
            if patient.dietitian != request.user:
                logger.warning(f"Patient {patient_id} belongs to {patient.dietitian.username}, not {request.user.username}")
                raise Http404("Patient not found or not assigned to you")
            
            diet_charts = DietChart.objects.filter(patient=patient).order_by('-created_at')
            
            # Get OCR reports if any (try to find user profile first)
            ocr_reports = []
            if patient.user_profile:
                from medical_ocr.models import MedicalDocument
                ocr_reports = MedicalDocument.objects.filter(doctor=patient.user_profile.user).order_by('-created_at')
            
            context = {
                'patient': patient,
                'patient_profile': None,  # No patient profile in old system
                'diet_charts': diet_charts,
                'ocr_reports': ocr_reports,
            }
            logger.info(f"Rendering patient detail for old system patient: {patient.name}")
            return render(request, 'diet_planner/patient_detail.html', context)
        else:
            logger.info(f"Patient {patient_id} not found in old system")
            
    except Patient.DoesNotExist:
        logger.info(f"Patient {patient_id} does not exist in old system")
    except Exception as e:
        logger.error(f"Error checking old system: {e}")
    
    # Fallback to new system (user_management)
    try:
        logger.info("Checking new system (user_management)")
        current_user_profile = UserProfile.objects.get(user=request.user)
        logger.info(f"Current user profile: {current_user_profile.user_type}")
        
        # Check if user profile exists
        user_profile_exists = UserProfile.objects.filter(id=patient_id, user_type='patient').exists()
        logger.info(f"User profile exists: {user_profile_exists}")
        
        if user_profile_exists:
            user_profile = UserProfile.objects.get(id=patient_id, user_type='patient')
            logger.info(f"User profile found: {user_profile.user.get_full_name()}")
            
            # Check for patient profile
            try:
                patient_profile = PatientProfile.objects.get(user_profile=user_profile)
                logger.info(f"Patient profile found, assigned doctor: {patient_profile.assigned_doctor}")
                
                # Check if this patient belongs to the current dietitian
                if patient_profile.assigned_doctor != current_user_profile:
                    logger.warning(f"Patient {patient_id} assigned to {patient_profile.assigned_doctor}, not {current_user_profile}")
                    raise Http404("Patient not found or not assigned to you")
                
                # Get diet charts for this patient
                diet_charts = DietChart.objects.filter(patient__user_profile=user_profile).order_by('-created_at')
                
                # Get OCR reports if any
                from medical_ocr.models import MedicalDocument
                ocr_reports = MedicalDocument.objects.filter(doctor=user_profile.user).order_by('-created_at')
                
                # Calculate age for display
                patient_age = calculate_age(user_profile.date_of_birth)
                
                context = {
                    'patient': user_profile,  # Use user_profile as patient
                    'patient_profile': patient_profile,
                    'patient_age': patient_age,
                    'diet_charts': diet_charts,
                    'ocr_reports': ocr_reports,
                }
                logger.info(f"Rendering patient detail for new system patient: {user_profile.user.get_full_name()}")
                return render(request, 'diet_planner/patient_detail.html', context)
                
            except PatientProfile.DoesNotExist:
                logger.warning(f"Patient profile not found for user profile {patient_id}")
                raise Http404("Patient profile not found")
        else:
            logger.warning(f"User profile {patient_id} not found in new system")
            
    except UserProfile.DoesNotExist:
        logger.warning(f"Current user profile not found for {request.user.username}")
    except Exception as e:
        logger.error(f"Error checking new system: {e}")
    
    # If we get here, patient was not found in either system
    logger.error(f"Patient {patient_id} not found in either system for user {request.user.username}")
    raise Http404("Patient not found")


@login_required
def create_patient(request):
    """Create a new patient with robust input validation - only for dietitians"""
    from user_management.models import UserProfile
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'dietitian':
            messages.error(request, 'Only dietitians can create patients.')
            return redirect('user_management:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('user_management:register')
    
    if request.method == 'POST':
        try:
            # Handle patient creation
            data = request.POST
            
            # Helper function to safely parse JSON fields
            def safe_json_parse(value, default=None):
                if default is None:
                    default = []
                if not value or value.strip() == '':
                    return default
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    # If JSON parsing fails, treat as comma-separated values
                    if isinstance(value, str):
                        return [item.strip() for item in value.split(',') if item.strip()]
                    return default
            
            # Helper function to safely parse numeric values
            def safe_float_parse(value, default=0.0, min_val=None, max_val=None):
                try:
                    val = float(value) if value else default
                    if min_val is not None and val < min_val:
                        return min_val
                    if max_val is not None and val > max_val:
                        return max_val
                    return val
                except (ValueError, TypeError):
                    return default
            
            def safe_int_parse(value, default=0, min_val=None, max_val=None):
                try:
                    val = int(value) if value else default
                    if min_val is not None and val < min_val:
                        return min_val
                    if max_val is not None and val > max_val:
                        return max_val
                    return val
                except (ValueError, TypeError):
                    return default
            
            # Validate and clean required fields
            name = data.get('name', '').strip()
            if not name:
                messages.error(request, 'Patient name is required.')
                return render(request, 'diet_planner/create_patient.html')
            
            # Validate numeric fields with safe defaults
            age = safe_int_parse(data.get('age'), 30, 1, 120)
            height = safe_float_parse(data.get('height'), 170.0, 50, 250)
            weight = safe_float_parse(data.get('weight'), 70.0, 20, 300)
            
            # Validate target weight if provided
            target_weight = None
            if data.get('target_weight'):
                target_weight = safe_float_parse(data.get('target_weight'), None, 20, 300)
            
            # Validate enum fields with safe defaults
            gender = data.get('gender', 'other')
            if gender not in ['male', 'female', 'other']:
                gender = 'other'
            
            prakriti = data.get('prakriti', 'tridoshic')
            if prakriti not in ['vata', 'pitta', 'kapha', 'vata_pitta', 'vata_kapha', 'pitta_kapha', 'tridoshic']:
                prakriti = 'tridoshic'
            
            activity_level = data.get('activity_level', 'sedentary')
            if activity_level not in ['sedentary', 'light', 'moderate', 'active', 'very_active']:
                activity_level = 'sedentary'
            
            # Create patient with validated data
            patient = Patient.objects.create(
                dietitian=request.user,
                name=name,
                age=age,
                gender=gender,
                height=height,
                weight=weight,
                prakriti=prakriti,
                vikriti=data.get('vikriti') or None,
                activity_level=activity_level,
                occupation=data.get('occupation', ''),
                allergies=safe_json_parse(data.get('allergies', '')),
                medical_conditions=safe_json_parse(data.get('medical_conditions', '')),
                medications=safe_json_parse(data.get('medications', '')),
                dietary_preferences=safe_json_parse(data.get('dietary_preferences', '')),
                food_dislikes=safe_json_parse(data.get('food_dislikes', '')),
                primary_goal=data.get('primary_goal', 'general_wellness'),
                target_weight=target_weight,
            )
            
            messages.success(request, f'Patient {patient.name} created successfully!')
            return redirect('diet_planner:patient_detail', patient_id=patient.id)
            
        except Exception as e:
            messages.error(request, f'Error creating patient: {str(e)}')
            form = PatientForm()
            context = {
                'form': form,
            }
            return render(request, 'diet_planner/create_patient.html', context)
    
    form = PatientForm()
    context = {
        'form': form,
    }
    return render(request, 'diet_planner/create_patient.html', context)


@login_required
def generate_diet_chart(request, patient_id):
    """Generate AI-powered diet chart for a patient based on analysis results"""
    from user_management.models import UserProfile, PatientProfile
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Generate diet chart request for patient ID: {patient_id}, User: {request.user.username}")
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'dietitian':
            messages.error(request, 'Only dietitians can generate diet charts.')
            return redirect('user_management:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('user_management:register')
    
    # First, try to get the patient from the old system (diet_planner.Patient)
    patient = None
    try:
        # Check if patient exists for any dietitian first
        patient_exists = Patient.objects.filter(id=patient_id).exists()
        logger.info(f"Patient exists in old system: {patient_exists}")
        
        if patient_exists:
            # Check if patient belongs to current user
            patient = Patient.objects.get(id=patient_id)
            logger.info(f"Patient found: {patient.name}, Dietitian: {patient.dietitian.username}")
            
            if patient.dietitian != request.user:
                logger.warning(f"Patient {patient_id} belongs to {patient.dietitian.username}, not {request.user.username}")
                raise Http404("Patient not found or not assigned to you")
        else:
            logger.info(f"Patient {patient_id} not found in old system")
            
    except Patient.DoesNotExist:
        logger.info(f"Patient {patient_id} does not exist in old system")
    except Exception as e:
        logger.error(f"Error checking old system: {e}")
    
    # If patient not found in old system, try new system
    if not patient:
        try:
            logger.info("Checking new system (user_management)")
            user_profile_patient = UserProfile.objects.get(id=patient_id, user_type='patient')
            logger.info(f"User profile found: {user_profile_patient.user.get_full_name()}")
            
            # Check for patient profile
            try:
                patient_profile = PatientProfile.objects.get(user_profile=user_profile_patient)
                logger.info(f"Patient profile found, assigned doctor: {patient_profile.assigned_doctor}")
                
                # Check if this patient belongs to the current dietitian
                if patient_profile.assigned_doctor != user_profile:
                    logger.warning(f"Patient {patient_id} assigned to {patient_profile.assigned_doctor}, not {user_profile}")
                    raise Http404("Patient not found or not assigned to you")
                
                # Create a proper Patient instance for compatibility
                try:
                    # Check if Patient already exists for this user_profile
                    patient = Patient.objects.get(user_profile=user_profile_patient)
                    logger.info(f"Found existing Patient instance: {patient.name}")
                except Patient.DoesNotExist:
                    # Create a new Patient instance with safe defaults
                    try:
                        # Safe data extraction
                        name = user_profile_patient.user.get_full_name() or user_profile_patient.user.username
                        age = calculate_age(user_profile_patient.date_of_birth)
                        gender = patient_profile.gender or 'other'
                        
                        # Safe numeric conversions
                        height = None
                        if patient_profile.height:
                            try:
                                height = float(patient_profile.height)
                            except (ValueError, TypeError):
                                height = None
                        
                        weight = None
                        if patient_profile.weight:
                            try:
                                weight = float(patient_profile.weight)
                            except (ValueError, TypeError):
                                weight = None
                        
                        # Safe list conversions
                        allergies = []
                        if patient_profile.allergies:
                            try:
                                allergies = [item.strip() for item in patient_profile.allergies.split(',') if item.strip()]
                            except (AttributeError, TypeError):
                                allergies = []
                        
                        medical_conditions = []
                        if patient_profile.medical_conditions:
                            try:
                                medical_conditions = [item.strip() for item in patient_profile.medical_conditions.split(',') if item.strip()]
                            except (AttributeError, TypeError):
                                medical_conditions = []
                        
                        medications = []
                        if patient_profile.current_medications:
                            try:
                                medications = [item.strip() for item in patient_profile.current_medications.split(',') if item.strip()]
                            except (AttributeError, TypeError):
                                medications = []
                        
                        patient = Patient.objects.create(
                            dietitian=user_profile.user,  # Current dietitian
                            user_profile=user_profile_patient,
                            name=name,
                            age=age,
                            gender=gender,
                            height=height,
                            weight=weight,
                            prakriti=patient_profile.dominant_dosha or 'tridosha',
                            activity_level='moderate',  # Default
                            allergies=allergies,
                            medical_conditions=medical_conditions,
                            medications=medications
                        )
                        logger.info(f"Created new Patient instance: {patient.name}")
                    except Exception as e:
                        logger.error(f"Error creating Patient instance: {e}")
                        raise
                
            except PatientProfile.DoesNotExist:
                logger.warning(f"Patient profile not found for user profile {patient_id}")
                raise Http404("Patient profile not found")
        except UserProfile.DoesNotExist:
            logger.warning(f"User profile {patient_id} not found in new system")
        except Exception as e:
            logger.error(f"Error checking new system: {e}")
    
    # If we still don't have a patient, raise 404
    if not patient:
        logger.error(f"Patient {patient_id} not found in either system for user {request.user.username}")
        raise Http404("Patient not found")
    
    # Check if patient has completed analysis
    analysis_completed = False
    patient_profile = None
    if hasattr(patient, 'user_profile') and patient.user_profile:
        try:
            patient_profile = PatientProfile.objects.get(user_profile=patient.user_profile)
            analysis_completed = (
                patient_profile.prakriti_analysis_completed and 
                patient_profile.disease_analysis_completed and 
                patient_profile.health_summary_generated
            )
        except PatientProfile.DoesNotExist:
            pass
    
    if not analysis_completed:
        if not patient.user_profile:
            # Try to find or create a user profile for this patient
            from user_management.models import UserProfile, PatientProfile
            
            # Generate a unique email for the patient
            email = f"patient_{patient.id}@nk360.com"
            
            try:
                from django.contrib.auth.models import User
                user = User.objects.get(email=email)
                user_profile = UserProfile.objects.get(user=user)
            except (User.DoesNotExist, UserProfile.DoesNotExist):
                try:
                    # Create a new user and profile
                    user = User.objects.create_user(
                        username=f"patient_{patient.id}",
                        email=email,
                        first_name=patient.name.split()[0] if patient.name else "Patient",
                        last_name=patient.name.split()[-1] if patient.name and len(patient.name.split()) > 1 else "",
                        password="temp_password_123"  # Temporary password
                    )
                    user_profile = UserProfile.objects.create(
                        user=user,
                        user_type='patient',
                        phone_number=""
                    )
                    PatientProfile.objects.create(user_profile=user_profile)
                except Exception as e:
                    messages.error(request, f'Error creating user profile: {str(e)}')
                    return redirect('diet_planner:patient_detail', patient_id=patient.id)
            
            # Link the patient to the user profile
            patient.user_profile = user_profile
            patient.save()
            
            messages.info(request, f'Created user profile for {patient.name}. Please complete the analysis.')
            return redirect('user_management:prakriti_analysis_patient', patient_id=user_profile.id)
        
        messages.warning(request, f'Please complete the analysis for {patient.name} before generating a diet chart.')
        return redirect('user_management:prakriti_analysis_patient', patient_id=patient.user_profile.id)
    
    # If analysis is completed, automatically generate the diet chart
    if analysis_completed and request.method == 'GET':
        try:
            # Check if patient has required data
            if not patient.height or not patient.weight or not patient.age:
                messages.error(request, "Patient must have height, weight, and age to generate diet chart.")
                return render(request, 'diet_planner/generate_diet_chart.html', {'patient': patient})
            
            # Check if there are foods in the database
            from diet_planner.models import Food
            food_count = Food.objects.filter(is_active=True).count()
            if food_count == 0:
                messages.error(request, "No foods available in database. Please import foods first.")
                return render(request, 'diet_planner/generate_diet_chart.html', {'patient': patient})
            
            # Use AI to generate diet chart
            architect_ai = DietArchitectAI()
            result = architect_ai.generate_diet_chart(patient)
            
            if result['success']:
                messages.success(request, f"AI-generated diet chart created successfully!")
                return redirect('diet_planner:diet_chart_detail', chart_id=result['diet_chart_id'])
            else:
                messages.error(request, f"Error generating diet chart: {result['error']}")
                
        except Exception as e:
            messages.error(request, f"Unexpected error generating diet chart: {str(e)}")
            print(f"DEBUG: Diet chart generation error: {e}")  # For debugging
    
    if request.method == 'POST':
        # Check if this is a patient data update request
        if 'update_patient' in request.POST:
            form = PatientBasicInfoForm(request.POST, instance=patient)
            if form.is_valid():
                form.save()
                messages.success(request, "Patient information updated successfully!")
                return redirect('diet_planner:generate_diet_chart', patient_id=patient_id)
            else:
                messages.error(request, "Please correct the errors below.")
                return render(request, 'diet_planner/generate_diet_chart.html', {
                    'patient': patient, 
                    'form': form,
                    'show_update_form': True
                })
        
        try:
            # Check if patient has required data
            if not patient.height or not patient.weight or not patient.age:
                messages.warning(request, "Please complete patient information before generating diet chart.")
                form = PatientBasicInfoForm(instance=patient)
                return render(request, 'diet_planner/generate_diet_chart.html', {
                    'patient': patient, 
                    'form': form,
                    'show_update_form': True
                })
            
            # Check if there are foods in the database
            from diet_planner.models import Food
            food_count = Food.objects.filter(is_active=True).count()
            if food_count == 0:
                messages.error(request, "No foods available in database. Please import foods first.")
                return render(request, 'diet_planner/generate_diet_chart.html', {'patient': patient})
            
            # Check if patient has completed analysis (if linked to user_management)
            analysis_completed = False
            if hasattr(patient, 'user_profile') and patient.user_profile:
                from user_management.models import PatientProfile
                try:
                    patient_profile = PatientProfile.objects.get(user_profile=patient.user_profile)
                    if patient_profile.prakriti_analysis_completed and patient_profile.disease_analysis_completed:
                        analysis_completed = True
                        # Update patient's prakriti based on analysis results
                        if patient_profile.dominant_dosha:
                            patient.prakriti = patient_profile.dominant_dosha
                            patient.save()
                        messages.info(request, f"Using analysis results: {patient_profile.dominant_dosha} constitution with {patient_profile.vata_percentage:.1f}% Vata, {patient_profile.pitta_percentage:.1f}% Pitta, {patient_profile.kapha_percentage:.1f}% Kapha")
                    else:
                        messages.warning(request, "Patient analysis not completed. Generating chart with basic information.")
                except PatientProfile.DoesNotExist:
                    messages.warning(request, "No analysis data found. Generating chart with basic information.")
            else:
                messages.warning(request, "No analysis data linked. Generating chart with basic information.")
            
            # Use AI #1 (The Architect) to generate diet chart
            architect_ai = DietArchitectAI()
            result = architect_ai.generate_diet_chart(patient)
            
            if result['success']:
                messages.success(request, f"AI-generated diet chart created successfully!")
                return redirect('diet_planner:diet_chart_detail', chart_id=result['diet_chart_id'])
            else:
                messages.error(request, f"Error generating diet chart: {result['error']}")
                
        except Exception as e:
            messages.error(request, f"Unexpected error generating diet chart: {str(e)}")
            print(f"DEBUG: Diet chart generation error: {e}")  # For debugging
    
    # Check if patient data is complete
    show_update_form = not (patient.height and patient.weight and patient.age)
    
    context = {
        'patient': patient,
        'user_profile': user_profile,
        'analysis_completed': analysis_completed,
        'patient_profile': patient_profile,
        'show_update_form': show_update_form,
        'form': PatientBasicInfoForm(instance=patient) if show_update_form else None,
    }
    return render(request, 'diet_planner/generate_diet_chart.html', context)


@login_required
def diet_chart_detail(request, chart_id):
    """View detailed diet chart - accessible by both dietitians and patients"""
    from user_management.models import UserProfile
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.user_type == 'patient':
            # Patient can only view their own diet charts
            diet_chart = get_object_or_404(DietChart, id=chart_id, patient__user_profile=user_profile)
        else:
            # Dietitian can view charts they created
            diet_chart = get_object_or_404(DietChart, id=chart_id, dietitian=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('user_management:register')
    
    meal_plans = MealPlan.objects.filter(diet_chart=diet_chart).order_by('day_number', 'meal_time')
    
    # Group meal plans by day
    days = {}
    for meal_plan in meal_plans:
        if meal_plan.day_number not in days:
            days[meal_plan.day_number] = {}
        days[meal_plan.day_number][meal_plan.meal_type] = meal_plan
    
    # Create days range for navigation
    days_range = range(1, diet_chart.duration_days + 1)
    
    # Get total foods count
    total_foods = Food.objects.filter(is_active=True).count()
    
    context = {
        'diet_chart': diet_chart,
        'days': days,
        'days_range': days_range,
        'meal_plans': meal_plans,
        'total_foods': total_foods,
        'is_patient': user_profile.user_type == 'patient',
    }
    return render(request, 'diet_planner/diet_chart_detail.html', context)

@login_required
def edit_diet_chart(request, chart_id):
    """Edit diet chart with CSV-based food selection"""
    diet_chart = get_object_or_404(DietChart, id=chart_id, dietitian=request.user)
    
    if request.method == 'POST':
        # Handle form submission for editing diet chart
        form_data = request.POST
        
        # Get all foods from database for selection
        all_foods = Food.objects.filter(is_active=True)
        
        # Process meal plan updates
        for key, value in form_data.items():
            if key.startswith('meal_item_'):
                meal_item_id = key.replace('meal_item_', '')
                try:
                    meal_item = MealItem.objects.get(id=meal_item_id, meal_plan__diet_chart=diet_chart)
                    # Update quantity if provided
                    if value and value.isdigit():
                        meal_item.quantity = int(value)
                        meal_item.save()
                except MealItem.DoesNotExist:
                    continue
        
        messages.success(request, 'Diet chart updated successfully!')
        return redirect('diet_planner:diet_chart_detail', chart_id=chart_id)
    
    # Get all foods for selection
    all_foods = Food.objects.filter(is_active=True).order_by('name')
    
    # Get meal plans
    meal_plans = MealPlan.objects.filter(diet_chart=diet_chart).order_by('day_number', 'meal_time')
    
    context = {
        'diet_chart': diet_chart,
        'all_foods': all_foods,
        'meal_plans': meal_plans,
        'days_range': range(1, diet_chart.duration_days + 1),
    }
    return render(request, 'diet_planner/edit_diet_chart.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def swap_food(request, meal_item_id):
    """Swap a food item using AI #2 (The Specialist)"""
    try:
        meal_item = get_object_or_404(MealItem, id=meal_item_id, meal_plan__diet_chart__dietitian=request.user)
        new_food_id = request.POST.get('new_food_id')
        
        if not new_food_id:
            return JsonResponse({'success': False, 'error': 'No food selected'})
        
        new_food = get_object_or_404(Food, id=new_food_id)
        
        # Log the swap
        swap_log = FoodSwapLog.objects.create(
            meal_item=meal_item,
            dietitian=request.user,
            original_food=meal_item.food,
            new_food=new_food,
            swap_reason=request.POST.get('reason', ''),
            similarity_score=0.8,  # This would be calculated by the AI
            ai_model_used='vector_similarity_specialist'
        )
        
        # Update the meal item
        meal_item.food = new_food
        meal_item.save()  # This will recalculate nutritional values
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully swapped {swap_log.original_food.name} with {swap_log.new_food.name}',
            'new_food': {
                'name': new_food.name,
                'calories': meal_item.calories,
                'protein': meal_item.protein,
                'carbs': meal_item.carbohydrates,
                'fat': meal_item.fat,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["GET"])
def get_similar_foods(request, meal_item_id):
    """Get similar foods for swapping using AI #2 (The Specialist)"""
    try:
        meal_item = get_object_or_404(MealItem, id=meal_item_id, meal_plan__diet_chart__dietitian=request.user)
        patient = meal_item.meal_plan.diet_chart.patient
        
        # Use AI #2 (The Specialist) to find similar foods
        specialist_ai = FoodSpecialistAI()
        similar_foods = specialist_ai.find_similar_foods(meal_item.food, patient)
        
        # Format response
        foods_data = []
        for item in similar_foods:
            foods_data.append({
                'id': str(item['food'].id),
                'name': item['food'].name,
                'category': item['food'].category,
                'calories': item['food'].calories,
                'protein': item['food'].protein,
                'carbs': item['food'].carbohydrates,
                'fat': item['food'].fat,
                'similarity_score': round(item['similarity_score'], 2),
                'reason': item['reason'],
                'ayurvedic_properties': {
                    'taste': item['food'].primary_taste,
                    'energy': item['food'].energy,
                    'vata_effect': item['food'].vata_effect,
                    'pitta_effect': item['food'].pitta_effect,
                    'kapha_effect': item['food'].kapha_effect,
                }
            })
        
        return JsonResponse({
            'success': True,
            'original_food': {
                'name': meal_item.food.name,
                'calories': meal_item.food.calories,
            },
            'similar_foods': foods_data,
            'ai_model': 'vector_similarity_specialist'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def food_database(request):
    """View and manage food database"""
    foods = Food.objects.filter(is_active=True)
    
    # Search and filter
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    if search_query:
        foods = foods.filter(name__icontains=search_query)
    
    if category_filter:
        foods = foods.filter(category=category_filter)
    
    # Get unique categories for filter
    categories = Food.objects.values_list('category', flat=True).distinct().order_by('category')
    
    # Pagination
    paginator = Paginator(foods, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
    }
    return render(request, 'diet_planner/food_database.html', context)


@login_required
def analytics(request):
    """Analytics for diet planning system"""
    # Get user's statistics
    total_patients = Patient.objects.filter(dietitian=request.user).count()
    total_charts = DietChart.objects.filter(dietitian=request.user).count()
    active_charts = DietChart.objects.filter(dietitian=request.user, status='active').count()
    total_swaps = FoodSwapLog.objects.filter(dietitian=request.user).count()
    
    # Get recent activity
    recent_charts = DietChart.objects.filter(dietitian=request.user).order_by('-created_at')[:5]
    recent_swaps = FoodSwapLog.objects.filter(dietitian=request.user).order_by('-created_at')[:5]
    
    context = {
        'total_patients': total_patients,
        'total_charts': total_charts,
        'active_charts': active_charts,
        'total_swaps': total_swaps,
        'recent_charts': recent_charts,
        'recent_swaps': recent_swaps,
    }
    return render(request, 'diet_planner/analytics.html', context)


@login_required
def import_foods_csv(request):
    """Import foods from CSV file"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        clear_existing = request.POST.get('clear_existing') == 'on'
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file to import.')
            return redirect('diet_planner:import_foods_csv')
        
        try:
            # Read and process CSV
            import csv
            import io
            
            # Decode the file
            file_data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_data))
            
            imported_count = 0
            error_count = 0
            errors = []
            
            # Clear existing foods if requested
            if clear_existing:
                Food.objects.all().delete()
                messages.info(request, 'Cleared all existing foods from database.')
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because of header
                try:
                    # Convert string boolean values to actual booleans
                    def str_to_bool(value):
                        if isinstance(value, str):
                            return value.lower() in ('true', '1', 'yes', 'on')
                        return bool(value)
                    
                    # Handle empty secondary_taste
                    secondary_taste = row.get('secondary_taste', '').strip()
                    if not secondary_taste:
                        secondary_taste = None
                    
                    # Handle both old and new CSV formats
                    food_name = row.get('Food Item') or row.get('name', '').strip()
                    if not food_name:
                        continue
                    
                    def safe_float(value):
                        try:
                            return float(value) if value else 0.0
                        except (ValueError, TypeError):
                            return 0.0
                    
                    def map_rasa(rasa):
                        if not rasa or rasa.strip() == '':
                            return 'sweet'
                        rasa = rasa.lower().strip()
                        rasa_mapping = {
                            'sweet': 'sweet', 'sweetness': 'sweet', 'madhura': 'sweet',
                            'sour': 'sour', 'sourness': 'sour', 'amla': 'sour',
                            'salty': 'salty', 'salt': 'salty', 'lavana': 'salty',
                            'pungent': 'pungent', 'spicy': 'pungent', 'katu': 'pungent', 'hot': 'pungent',
                            'bitter': 'bitter', 'bitterness': 'bitter', 'tikta': 'bitter',
                            'astringent': 'astringent', 'kashaya': 'astringent', 'dry': 'astringent',
                        }
                        return rasa_mapping.get(rasa, 'sweet')
                    
                    def map_virya(virya):
                        if not virya or virya.strip() == '':
                            return 'neutral'
                        virya = virya.lower().strip()
                        virya_mapping = {
                            'hot': 'heating', 'heating': 'heating', 'warm': 'heating', 'ushna': 'heating',
                            'cold': 'cooling', 'cooling': 'cooling', 'cool': 'cooling', 'sheeta': 'cooling',
                            'neutral': 'neutral', 'moderate': 'neutral', 'balanced': 'neutral',
                        }
                        return virya_mapping.get(virya, 'neutral')
                    
                    def map_dosha_effect(effect):
                        if not effect or effect.strip() == '':
                            return 'neutral'
                        effect = effect.lower().strip()
                        effect_mapping = {
                            'increase': 'aggravates', 'aggravate': 'aggravates', 'aggravates': 'aggravates',
                            'decrease': 'pacifies', 'pacify': 'pacifies', 'pacifies': 'pacifies',
                            'neutral': 'neutral', 'moderate': 'neutral', 'balanced': 'neutral',
                        }
                        return effect_mapping.get(effect, 'neutral')
                    
                    food_data = {
                        'name': food_name,
                        'category': row.get('Category') or row.get('category', 'other').strip(),
                        'subcategory': row.get('Meal Type') or row.get('subcategory', '').strip() or None,
                        'calories': int(safe_float(row.get('Calories (k)') or row.get('calories', 0))),
                        'protein': safe_float(row.get('Protein (g)') or row.get('protein', 0)),
                        'carbohydrates': safe_float(row.get('Carbs (g)') or row.get('carbohydrates', 0)),
                        'fat': safe_float(row.get('Fat (g)') or row.get('fat', 0)),
                        'fiber': safe_float(row.get('Fibre (g)') or row.get('fiber', 0)),
                        'primary_taste': map_rasa(row.get('Rasa') or row.get('primary_taste', 'sweet')),
                        'secondary_taste': None,
                        'energy': map_virya(row.get('Virya') or row.get('energy', 'neutral')),
                        'vata_effect': map_dosha_effect(row.get('Vata Effect') or row.get('vata_effec') or row.get('Dosha Effect') or row.get('vata_effect', 'neutral')),
                        'pitta_effect': map_dosha_effect(row.get('Pitta Effect') or row.get('pitta_effe') or row.get('Dosha Effect') or row.get('pitta_effect', 'neutral')),
                        'kapha_effect': map_dosha_effect(row.get('Kapha Effect') or row.get('kapha_eff') or row.get('Dosha Effect') or row.get('kapha_effect', 'neutral')),
                        'is_vegetarian': str_to_bool(row.get('is_vegetarian', 'True')),
                        'is_vegan': str_to_bool(row.get('is_vegan', 'True')),
                        'is_gluten_free': str_to_bool(row.get('is_gluten_free', 'True')),
                        'is_dairy_free': str_to_bool(row.get('is_dairy_free', 'True')),
                        'contains_nuts': str_to_bool(row.get('contains_nuts', 'False')),
                        'contains_soy': str_to_bool(row.get('contains_soy', 'False')),
                        'contains_eggs': str_to_bool(row.get('contains_eggs', 'False')),
                        'contains_fish': str_to_bool(row.get('contains_fish', 'False')),
                        'contains_shellfish': str_to_bool(row.get('contains_shellfish', 'False')),
                    }
                    
                    # Create or update food
                    food, created = Food.objects.get_or_create(
                        name=food_data['name'],
                        defaults=food_data
                    )
                    
                    if created:
                        imported_count += 1
                    else:
                        # Update existing food with new data
                        for key, value in food_data.items():
                            if key != 'name':  # Don't update the name
                                setattr(food, key, value)
                        food.save()
                        imported_count += 1
                        
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue
            
            # Show results
            if imported_count > 0:
                messages.success(request, f'Successfully imported {imported_count} foods!')
            
            if error_count > 0:
                messages.warning(request, f'Encountered {error_count} errors during import.')
                # Show first few errors
                for error in errors[:5]:
                    messages.error(request, error)
                if len(errors) > 5:
                    messages.info(request, f'... and {len(errors) - 5} more errors.')
            
            total_foods = Food.objects.count()
            messages.info(request, f'Total foods in database: {total_foods}')
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
    
    # Get database statistics
    total_foods = Food.objects.count()
    active_foods = Food.objects.filter(is_active=True).count()
    categories_count = Food.objects.values('category').distinct().count()
    
    context = {
        'total_foods': total_foods,
        'active_foods': active_foods,
        'categories_count': categories_count,
    }
    
    return render(request, 'diet_planner/import_foods_csv.html', context)


@login_required
def download_sample_csv(request):
    """Download sample CSV file"""
    from django.http import HttpResponse
    
    # Sample CSV content
    csv_content = """name,category,subcategory,calories,protein,carbohydrates,fat,fiber,primary_taste,secondary_taste,energy,vata_effect,pitta_effect,kapha_effect,is_vegetarian,is_vegan,is_gluten_free,is_dairy_free,contains_nuts,contains_soy,contains_eggs,contains_fish,contains_shellfish
Basmati Rice,grains,white_rice,130,2.7,28.0,0.3,0.4,sweet,,cooling,pacifies,pacifies,aggravates,True,True,True,True,False,False,False,False,False
Brown Rice,grains,brown_rice,111,2.6,23.0,0.9,1.8,sweet,,cooling,pacifies,pacifies,aggravates,True,True,True,True,False,False,False,False,False
Quinoa,grains,pseudo_grains,120,4.4,22.0,1.9,2.8,sweet,astringent,cooling,pacifies,pacifies,neutral,True,True,True,True,False,False,False,False,False
Spinach,vegetables,leafy_greens,23,2.9,3.6,0.4,2.2,bitter,astringent,cooling,aggravates,pacifies,pacifies,True,True,True,True,False,False,False,False,False
Kale,vegetables,leafy_greens,49,4.3,8.8,0.9,3.6,bitter,astringent,cooling,aggravates,pacifies,pacifies,True,True,True,True,False,False,False,False,False
Sweet Potato,vegetables,root_vegetables,86,1.6,20.1,0.1,3.0,sweet,,heating,pacifies,aggravates,aggravates,True,True,True,True,False,False,False,False,False
Carrot,vegetables,root_vegetables,41,0.9,9.6,0.2,2.8,sweet,,cooling,pacifies,pacifies,neutral,True,True,True,True,False,False,False,False,False
Apple,fruits,pome_fruits,52,0.3,13.8,0.2,2.4,sweet,astringent,cooling,pacifies,pacifies,aggravates,True,True,True,True,False,False,False,False,False
Banana,fruits,tropical_fruits,89,1.1,22.8,0.3,2.6,sweet,,cooling,pacifies,pacifies,aggravates,True,True,True,True,False,False,False,False,False
Orange,fruits,citrus_fruits,47,0.9,11.8,0.1,2.4,sour,sweet,cooling,aggravates,pacifies,neutral,True,True,True,True,False,False,False,False,False
Lentils (Red),proteins,legumes,116,9.0,20.1,0.4,7.9,sweet,astringent,heating,pacifies,aggravates,neutral,True,True,True,True,False,False,False,False,False
Chickpeas,proteins,legumes,164,8.9,27.4,2.6,7.6,sweet,astringent,heating,pacifies,aggravates,neutral,True,True,True,True,False,False,False,False,False
Almonds,proteins,nuts,579,21.2,21.6,49.9,12.5,sweet,,heating,pacifies,aggravates,aggravates,True,True,True,True,True,False,False,False,False
Ghee,dairy,fats,900,0.0,0.0,100.0,0.0,sweet,,heating,pacifies,aggravates,aggravates,True,False,True,False,False,False,False,False,False
Yogurt,dairy,fermented,59,10.0,3.6,0.4,0.0,sour,sweet,cooling,aggravates,pacifies,aggravates,True,False,True,False,False,False,False,False,False
Turmeric,spices,roots,354,7.8,64.9,9.9,21.1,bitter,pungent,heating,pacifies,pacifies,pacifies,True,True,True,True,False,False,False,False,False
Ginger,spices,roots,80,1.8,17.8,0.8,2.0,pungent,sweet,heating,pacifies,aggravates,pacifies,True,True,True,True,False,False,False,False,False"""
    
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_foods.csv"'
    return response


@login_required
def import_custom_foods_csv(request):
    """Import foods from custom CSV format"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        clear_existing = request.POST.get('clear_existing') == 'on'
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file to import.')
            return redirect('diet_planner:import_custom_foods_csv')
        
        try:
            # Read and process CSV
            import csv
            import io
            
            # Decode the file
            file_data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_data))
            
            imported_count = 0
            error_count = 0
            errors = []
            
            # Clear existing foods if requested
            if clear_existing:
                Food.objects.all().delete()
                messages.info(request, 'Cleared all existing foods from database.')
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because of header
                try:
                    # Map your CSV format to our database format
                    def safe_float(value):
                        try:
                            return float(value) if value else 0.0
                        except (ValueError, TypeError):
                            return 0.0
                    
                    def map_rasa(rasa):
                        if not rasa or rasa.strip() == '':
                            return 'sweet'
                        
                        rasa = rasa.lower().strip()
                        rasa_mapping = {
                            'sweet': 'sweet', 'sweetness': 'sweet', 'madhura': 'sweet',
                            'sour': 'sour', 'sourness': 'sour', 'amla': 'sour',
                            'salty': 'salty', 'salt': 'salty', 'lavana': 'salty',
                            'pungent': 'pungent', 'spicy': 'pungent', 'katu': 'pungent', 'hot': 'pungent',
                            'bitter': 'bitter', 'bitterness': 'bitter', 'tikta': 'bitter',
                            'astringent': 'astringent', 'kashaya': 'astringent', 'dry': 'astringent',
                        }
                        return rasa_mapping.get(rasa, 'sweet')
                    
                    def map_virya(virya):
                        if not virya or virya.strip() == '':
                            return 'neutral'
                        
                        virya = virya.lower().strip()
                        virya_mapping = {
                            'hot': 'heating', 'heating': 'heating', 'warm': 'heating', 'ushna': 'heating',
                            'cold': 'cooling', 'cooling': 'cooling', 'cool': 'cooling', 'sheeta': 'cooling',
                            'neutral': 'neutral', 'moderate': 'neutral', 'balanced': 'neutral',
                        }
                        return virya_mapping.get(virya, 'neutral')
                    
                    def map_dosha_effect(effect):
                        if not effect or effect.strip() == '':
                            return 'neutral'
                        
                        effect = effect.lower().strip()
                        effect_mapping = {
                            'increase': 'aggravates', 'aggravate': 'aggravates', 'aggravates': 'aggravates',
                            'decrease': 'pacifies', 'pacify': 'pacifies', 'pacifies': 'pacifies',
                            'neutral': 'neutral', 'moderate': 'neutral', 'balanced': 'neutral',
                        }
                        return effect_mapping.get(effect, 'neutral')
                    
                    # Handle both old and new CSV formats
                    food_name = row.get('Food Item') or row.get('name', '').strip()
                    if not food_name:
                        continue
                    
                    food_data = {
                        'name': food_name,
                        'category': row.get('Category') or row.get('food_cate', 'other').strip(),
                        'subcategory': row.get('Meal Type') or row.get('meal_type', '').strip() or None,
                        'calories': int(safe_float(row.get('Calories (k)') or row.get('calories', 0))),
                        'protein': safe_float(row.get('Protein (g)') or row.get('protein_g', 0)),
                        'carbohydrates': safe_float(row.get('Carbs (g)') or row.get('carbohydr', 0)),
                        'fat': safe_float(row.get('Fat (g)') or row.get('fat_g', 0)),
                        'fiber': safe_float(row.get('Fibre (g)') or row.get('fiber', 0)),
                        'primary_taste': map_rasa(row.get('Rasa') or row.get('rasa', 'sweet')),
                        'secondary_taste': None,
                        'energy': map_virya(row.get('Virya') or row.get('virya', 'neutral')),
                        'vata_effect': map_dosha_effect(row.get('Vata Effect') or row.get('vata_effec') or row.get('Dosha Effect') or row.get('vata_effect', 'neutral')),
                        'pitta_effect': map_dosha_effect(row.get('Pitta Effect') or row.get('pitta_effe') or row.get('Dosha Effect') or row.get('pitta_effect', 'neutral')),
                        'kapha_effect': map_dosha_effect(row.get('Kapha Effect') or row.get('kapha_eff') or row.get('Dosha Effect') or row.get('kapha_effect', 'neutral')),
                        'is_vegetarian': True,
                        'is_vegan': True,
                        'is_gluten_free': True,
                        'is_dairy_free': True,
                        'contains_nuts': False,
                        'contains_soy': False,
                        'contains_eggs': False,
                        'contains_fish': False,
                        'contains_shellfish': False,
                    }
                    
                    # Create or update the food object
                    food, created = Food.objects.get_or_create(
                        name=food_data['name'],
                        defaults=food_data
                    )
                    
                    if created:
                        imported_count += 1
                    else:
                        # Update existing food with new data
                        for key, value in food_data.items():
                            if key != 'name':  # Don't update the name
                                setattr(food, key, value)
                        food.save()
                        imported_count += 1
                    
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Only show first 5 errors
                        messages.error(request, f'Row {row_num}: {str(e)}')
                    elif error_count == 6:
                        messages.info(request, f'... and {error_count - 5} more errors.')
                    
                    logger.error(f'Error importing row {row_num}: {str(e)}')
            
            messages.success(request, f'Successfully imported {imported_count} foods!')
            if error_count > 0:
                messages.warning(request, f'Encountered {error_count} errors during import.')
            
            # Show total count
            total_foods = Food.objects.count()
            messages.info(request, f'Total foods in database: {total_foods}')
            
        except Exception as e:
            messages.error(request, f'Error reading CSV file: {str(e)}')
            logger.error(f'Error reading CSV file: {str(e)}')
    
    return render(request, 'diet_planner/import_custom_foods_csv.html')


# Recipe Views
@login_required
def recipe_list(request):
    """List all recipes"""
    recipes = Recipe.objects.filter(is_active=True, is_public=True).order_by('name')
    
    # Filter by food if specified
    food_id = request.GET.get('food_id')
    if food_id:
        recipes = recipes.filter(food_id=food_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        recipes = recipes.filter(
            Q(name__icontains=search_query) |
            Q(food__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(recipes, 12)
    page_number = request.GET.get('page')
    recipes = paginator.get_page(page_number)
    
    context = {
        'recipes': recipes,
        'search_query': search_query,
        'food_id': food_id,
    }
    return render(request, 'diet_planner/recipe_list.html', context)


@login_required
def recipe_detail(request, recipe_id):
    """Detailed view of a recipe"""
    recipe = get_object_or_404(Recipe, id=recipe_id, is_active=True, is_public=True)
    
    context = {
        'recipe': recipe,
    }
    return render(request, 'diet_planner/recipe_detail.html', context)


@login_required
def food_recipes(request, food_id):
    """Show all recipes for a specific food"""
    food = get_object_or_404(Food, id=food_id)
    recipes = Recipe.objects.filter(food=food, is_active=True, is_public=True).order_by('name')
    
    context = {
        'food': food,
        'recipes': recipes,
    }
    return render(request, 'diet_planner/food_recipes.html', context)


@login_required
def diet_chart_with_recipes(request, chart_id):
    """Diet chart view with recipe links"""
    chart = get_object_or_404(DietChart, id=chart_id, dietitian=request.user)
    
    # Get all meal items with their recipes
    meal_items = MealItem.objects.filter(meal_plan__diet_chart=chart).select_related('food')
    
    # Get recipes for each food
    food_recipes_map = {}
    for item in meal_items:
        if item.food not in food_recipes_map:
            recipes = Recipe.objects.filter(
                food=item.food, 
                is_active=True, 
                is_public=True
            ).order_by('name')
            food_recipes_map[item.food] = recipes
    
    context = {
        'chart': chart,
        'meal_items': meal_items,
        'food_recipes_map': food_recipes_map,
    }
    return render(request, 'diet_planner/diet_chart_with_recipes.html', context)


@login_required
def generate_recipe_chat(request, food_id):
    """Generate recipe using Recipe Generator AI for a specific food"""
    from .recipe_service import RecipeGeneratorAI
    
    food = get_object_or_404(Food, id=food_id)
    
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        
        if user_message:
            try:
                # Initialize Recipe Generator AI
                recipe_ai = RecipeGeneratorAI()
                
                # Prepare food details
                food_details = {
                    'category': food.category,
                    'calories': food.calories,
                    'protein': food.protein,
                    'carbohydrates': food.carbohydrates,
                    'fat': food.fat,
                    'primary_taste': food.get_primary_taste_display(),
                    'energy': food.get_energy_display(),
                    'vata_effect': food.get_vata_effect_display(),
                    'pitta_effect': food.get_pitta_effect_display(),
                    'kapha_effect': food.get_kapha_effect_display(),
                }
                
                # Generate recipe
                response = recipe_ai.generate_recipe(food.name, food_details, user_message)
                
                return JsonResponse({
                    'success': response['success'],
                    'response': response['content'],
                    'confidence': response.get('confidence', 0.8),
                    'is_medical_advice': False,
                    'youtube_url': response.get('youtube_url', ''),
                    'youtube_search': response.get('youtube_search', '')
                })
                
            except Exception as e:
                logger.error(f"Error generating recipe: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error generating recipe: {str(e)}'
                })
    
    # Default recipe generation prompt
    default_prompt = f"Generate a healthy and delicious recipe for {food.name} with Ayurvedic guidelines"
    
    context = {
        'food': food,
        'default_prompt': default_prompt,
    }
    return render(request, 'diet_planner/recipe_chat.html', context)


@login_required
def generate_recipe_ai(request, food_id):
    """Generate recipe using AI with YouTube URL"""
    try:
        food = get_object_or_404(Food, id=food_id, is_active=True)
        
        if request.method == 'POST':
            meal_type = request.POST.get('meal_type', 'lunch')
            
            # Use RecipeGeneratorAI to generate recipe
            recipe_ai = RecipeGeneratorAI()
            result = recipe_ai.generate_recipe(food, meal_type, request.user)
            
            if result['success']:
                messages.success(request, result['message'])
                return redirect('diet_planner:recipe_detail', recipe_id=result['recipe_id'])
            else:
                messages.error(request, result['error'])
                return redirect('diet_planner:food_recipes', food_id=food_id)
        
        # GET request - show form
        context = {
            'food': food,
            'meal_types': [
                ('breakfast', 'Breakfast'),
                ('lunch', 'Lunch'),
                ('dinner', 'Dinner'),
                ('snack', 'Snack'),
            ]
        }
        return render(request, 'diet_planner/generate_recipe_ai.html', context)
        
    except Exception as e:
        logger.error(f"Error in generate_recipe_ai: {e}")
        messages.error(request, f"Error generating recipe: {str(e)}")
        return redirect('diet_planner:food_database')
    food_recipes_map = {}
    for item in meal_items:
        if item.food not in food_recipes_map:
            recipes = Recipe.objects.filter(
                food=item.food, 
                is_active=True, 
                is_public=True
            ).order_by('name')
            food_recipes_map[item.food] = recipes
    
    context = {
        'chart': chart,
        'meal_items': meal_items,
        'food_recipes_map': food_recipes_map,
    }
    return render(request, 'diet_planner/diet_chart_with_recipes.html', context)


@login_required
def generate_recipe_chat(request, food_id):
    """Generate recipe using Recipe Generator AI for a specific food"""
    from .recipe_service import RecipeGeneratorAI
    
    food = get_object_or_404(Food, id=food_id)
    
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        
        if user_message:
            try:
                # Initialize Recipe Generator AI
                recipe_ai = RecipeGeneratorAI()
                
                # Prepare food details
                food_details = {
                    'category': food.category,
                    'calories': food.calories,
                    'protein': food.protein,
                    'carbohydrates': food.carbohydrates,
                    'fat': food.fat,
                    'primary_taste': food.get_primary_taste_display(),
                    'energy': food.get_energy_display(),
                    'vata_effect': food.get_vata_effect_display(),
                    'pitta_effect': food.get_pitta_effect_display(),
                    'kapha_effect': food.get_kapha_effect_display(),
                }
                
                # Generate recipe
                response = recipe_ai.generate_recipe(food.name, food_details, user_message)
                
                return JsonResponse({
                    'success': response['success'],
                    'response': response['content'],
                    'confidence': response.get('confidence', 0.8),
                    'is_medical_advice': False,
                    'youtube_url': response.get('youtube_url', ''),
                    'youtube_search': response.get('youtube_search', '')
                })
                
            except Exception as e:
                logger.error(f"Error generating recipe: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error generating recipe: {str(e)}'
                })
    
    # Default recipe generation prompt
    default_prompt = f"Generate a healthy and delicious recipe for {food.name} with Ayurvedic guidelines"
    
    context = {
        'food': food,
        'default_prompt': default_prompt,
    }
    return render(request, 'diet_planner/recipe_chat.html', context)


@login_required
def generate_recipe_ai(request, food_id):
    """Generate recipe using AI with YouTube URL"""
    try:
        food = get_object_or_404(Food, id=food_id, is_active=True)
        
        if request.method == 'POST':
            meal_type = request.POST.get('meal_type', 'lunch')
            
            # Use RecipeGeneratorAI to generate recipe
            recipe_ai = RecipeGeneratorAI()
            result = recipe_ai.generate_recipe(food, meal_type, request.user)
            
            if result['success']:
                messages.success(request, result['message'])
                return redirect('diet_planner:recipe_detail', recipe_id=result['recipe_id'])
            else:
                messages.error(request, result['error'])
                return redirect('diet_planner:food_recipes', food_id=food_id)
        
        # GET request - show form
        context = {
            'food': food,
            'meal_types': [
                ('breakfast', 'Breakfast'),
                ('lunch', 'Lunch'),
                ('dinner', 'Dinner'),
                ('snack', 'Snack'),
            ]
        }
        return render(request, 'diet_planner/generate_recipe_ai.html', context)
        
    except Exception as e:
        logger.error(f"Error in generate_recipe_ai: {e}")
        messages.error(request, f"Error generating recipe: {str(e)}")
        return redirect('diet_planner:food_database')