from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from diet_planner.models import Patient
from user_management.models import UserProfile, PatientProfile
import uuid

class Command(BaseCommand):
    help = 'Check specific patient and fix issues'

    def handle(self, *args, **options):
        patient_id = "b13e11b2-f159-4e4e-b17b-e64fc40a9303"
        self.stdout.write(f"Checking patient ID: {patient_id}")
        
        try:
            patient_uuid = uuid.UUID(patient_id)
            self.stdout.write(f"✓ Valid UUID: {patient_uuid}")
        except ValueError:
            self.stdout.write(self.style.ERROR(f"✗ Invalid UUID: {patient_id}"))
            return
        
        # Check in old system
        self.stdout.write("\n=== Old System Check ===")
        try:
            patient = Patient.objects.get(id=patient_uuid)
            self.stdout.write(self.style.SUCCESS(f"✓ Found patient: {patient.name}"))
            self.stdout.write(f"  - Dietitian: {patient.dietitian.username}")
            self.stdout.write(f"  - User Profile: {patient.user_profile}")
            self.stdout.write(f"  - Age: {patient.age}")
            self.stdout.write(f"  - Gender: {patient.gender}")
            
            # Check if patient belongs to current user
            current_user = User.objects.get(username='Kabi12211')  # From the logs
            self.stdout.write(f"  - Current user: {current_user.username}")
            self.stdout.write(f"  - Patient belongs to current user: {patient.dietitian == current_user}")
            
            if patient.dietitian != current_user:
                self.stdout.write(self.style.WARNING("  ⚠️  Patient belongs to different dietitian!"))
                self.stdout.write(f"  - To fix: Either login as {patient.dietitian.username} or reassign patient")
            
        except Patient.DoesNotExist:
            self.stdout.write(self.style.WARNING("✗ Patient not found in old system"))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING("✗ Current user not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {e}"))
        
        # Check in new system
        self.stdout.write("\n=== New System Check ===")
        try:
            user_profile = UserProfile.objects.get(id=patient_uuid, user_type='patient')
            self.stdout.write(self.style.SUCCESS(f"✓ Found user profile: {user_profile.user.get_full_name()}"))
            self.stdout.write(f"  - User: {user_profile.user.username}")
            self.stdout.write(f"  - Email: {user_profile.user.email}")
            
            try:
                patient_profile = PatientProfile.objects.get(user_profile=user_profile)
                self.stdout.write(f"  - Patient Profile: ✓ Found")
                self.stdout.write(f"  - Assigned Doctor: {patient_profile.assigned_doctor}")
            except PatientProfile.DoesNotExist:
                self.stdout.write("  - Patient Profile: ✗ Not found")
                
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.WARNING("✗ User profile not found in new system"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {e}"))
        
        # List all patients for current user
        self.stdout.write("\n=== All Patients for Current User ===")
        try:
            current_user = User.objects.get(username='Kabi12211')
            patients = Patient.objects.filter(dietitian=current_user)
            self.stdout.write(f"Found {patients.count()} patients for {current_user.username}:")
            for patient in patients:
                self.stdout.write(f"  - {patient.id}: {patient.name}")
        except User.DoesNotExist:
            self.stdout.write("Current user not found")
        except Exception as e:
            self.stdout.write(f"Error: {e}")
        
        # Recommendations
        self.stdout.write("\n=== Recommendations ===")
        try:
            current_user = User.objects.get(username='Kabi12211')
            patients = Patient.objects.filter(dietitian=current_user)
            
            if patients.exists():
                self.stdout.write("✓ You have patients assigned to you. Try accessing:")
                for patient in patients:
                    self.stdout.write(f"  - http://127.0.0.1:8000/diet-planner/patients/{patient.id}/")
            else:
                self.stdout.write("⚠️  No patients assigned to you. You may need to:")
                self.stdout.write("  1. Create a new patient")
                self.stdout.write("  2. Or have an admin reassign existing patients to you")
                
        except User.DoesNotExist:
            self.stdout.write("Current user not found")
