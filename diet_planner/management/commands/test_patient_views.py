from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from diet_planner.models import Patient
from user_management.models import UserProfile, PatientProfile
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from diet_planner.views import patient_list, patient_detail, calculate_age
import uuid

class Command(BaseCommand):
    help = 'Test patient views functionality'

    def handle(self, *args, **options):
        self.stdout.write("Testing patient views...")
        
        # Test calculate_age function
        self.stdout.write("\n=== Testing calculate_age function ===")
        from datetime import date
        test_date = date(1990, 1, 1)
        age = calculate_age(test_date)
        self.stdout.write(f"Age calculation test: {age} years (expected: {date.today().year - 1990})")
        
        # Test patient list view
        self.stdout.write("\n=== Testing patient list view ===")
        try:
            # Get a dietitian user
            dietitian_users = User.objects.filter(profile__user_type='dietitian')
            if dietitian_users.exists():
                user = dietitian_users.first()
                self.stdout.write(f"Testing with dietitian: {user.username}")
                
                # Create a mock request
                factory = RequestFactory()
                request = factory.get('/diet-planner/patients/')
                request.user = user
                
                # Test the view
                response = patient_list(request)
                self.stdout.write(f"Patient list view status: {response.status_code}")
                if response.status_code == 200:
                    self.stdout.write("✓ Patient list view working correctly")
                else:
                    self.stdout.write(f"✗ Patient list view failed with status {response.status_code}")
            else:
                self.stdout.write("No dietitian users found")
                
        except Exception as e:
            self.stdout.write(f"✗ Error testing patient list view: {e}")
        
        # Test patient detail view with debug
        self.stdout.write("\n=== Testing patient detail view ===")
        try:
            # Get a patient ID to test with
            patients = Patient.objects.all()
            if patients.exists():
                patient = patients.first()
                self.stdout.write(f"Testing with patient: {patient.name} (ID: {patient.id})")
                
                # Create a mock request
                factory = RequestFactory()
                request = factory.get(f'/diet-planner/patients/{patient.id}/')
                request.user = patient.dietitian
                
                # Test the view
                response = patient_detail(request, patient.id)
                self.stdout.write(f"Patient detail view status: {response.status_code}")
                if response.status_code == 200:
                    self.stdout.write("✓ Patient detail view working correctly")
                else:
                    self.stdout.write(f"✗ Patient detail view failed with status {response.status_code}")
            else:
                self.stdout.write("No patients found")
                
        except Exception as e:
            self.stdout.write(f"✗ Error testing patient detail view: {e}")
        
        # List all patients and user profiles
        self.stdout.write("\n=== Database Summary ===")
        self.stdout.write(f"Total patients (old system): {Patient.objects.count()}")
        self.stdout.write(f"Total user profiles: {UserProfile.objects.count()}")
        self.stdout.write(f"Total patient profiles: {PatientProfile.objects.count()}")
        
        self.stdout.write("\n=== All Patients ===")
        for patient in Patient.objects.all():
            self.stdout.write(f"  - {patient.id}: {patient.name} (Dietitian: {patient.dietitian.username})")
        
        self.stdout.write("\n=== All User Profiles ===")
        for profile in UserProfile.objects.all():
            self.stdout.write(f"  - {profile.id}: {profile.user.get_full_name()} ({profile.user_type})")
        
        self.stdout.write("\nTest completed!")
