from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from diet_planner.models import Patient
from user_management.models import UserProfile, PatientProfile
import uuid

class Command(BaseCommand):
    help = 'Debug patient lookup issues'

    def add_arguments(self, parser):
        parser.add_argument('patient_id', type=str, help='Patient ID to debug')

    def handle(self, *args, **options):
        patient_id = options['patient_id']
        self.stdout.write(f"Debugging patient ID: {patient_id}")
        
        try:
            # Try to parse as UUID
            patient_uuid = uuid.UUID(patient_id)
            self.stdout.write(f"Valid UUID: {patient_uuid}")
        except ValueError:
            self.stdout.write(self.style.ERROR(f"Invalid UUID: {patient_id}"))
            return
        
        # Check in old system (diet_planner.Patient)
        self.stdout.write("\n=== Checking Old System (diet_planner.Patient) ===")
        try:
            patient = Patient.objects.get(id=patient_uuid)
            self.stdout.write(self.style.SUCCESS(f"Found patient in old system: {patient.name}"))
            self.stdout.write(f"  - Dietitian: {patient.dietitian.username}")
            self.stdout.write(f"  - User Profile: {patient.user_profile}")
            self.stdout.write(f"  - Age: {patient.age}")
            self.stdout.write(f"  - Gender: {patient.gender}")
        except Patient.DoesNotExist:
            self.stdout.write(self.style.WARNING("Patient not found in old system"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error checking old system: {e}"))
        
        # Check in new system (user_management.UserProfile)
        self.stdout.write("\n=== Checking New System (user_management.UserProfile) ===")
        try:
            user_profile = UserProfile.objects.get(id=patient_uuid, user_type='patient')
            self.stdout.write(self.style.SUCCESS(f"Found user profile: {user_profile.user.get_full_name()}"))
            self.stdout.write(f"  - User: {user_profile.user.username}")
            self.stdout.write(f"  - Email: {user_profile.user.email}")
            
            # Check for patient profile
            try:
                patient_profile = PatientProfile.objects.get(user_profile=user_profile)
                self.stdout.write(f"  - Patient Profile: Found")
                self.stdout.write(f"  - Assigned Doctor: {patient_profile.assigned_doctor}")
                self.stdout.write(f"  - Age: {patient_profile.age}")
                self.stdout.write(f"  - Gender: {patient_profile.gender}")
            except PatientProfile.DoesNotExist:
                self.stdout.write(self.style.WARNING("  - Patient Profile: Not found"))
                
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.WARNING("User profile not found in new system"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error checking new system: {e}"))
        
        # Check all patients for the current user
        self.stdout.write("\n=== All Patients for Current User ===")
        try:
            # Get all users to check
            users = User.objects.all()
            for user in users:
                if user.patients.exists():
                    self.stdout.write(f"User {user.username} has {user.patients.count()} patients:")
                    for patient in user.patients.all():
                        self.stdout.write(f"  - {patient.id}: {patient.name}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error listing patients: {e}"))
        
        # Check all user profiles
        self.stdout.write("\n=== All User Profiles ===")
        try:
            user_profiles = UserProfile.objects.filter(user_type='patient')
            self.stdout.write(f"Found {user_profiles.count()} patient user profiles:")
            for profile in user_profiles:
                self.stdout.write(f"  - {profile.id}: {profile.user.get_full_name()}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error listing user profiles: {e}"))
