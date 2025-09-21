#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from diet_planner.models import Patient
from user_management.models import UserProfile, PatientProfile
import uuid

def check_patient(patient_id):
    print(f"Checking patient ID: {patient_id}")
    
    try:
        # Try to parse as UUID
        patient_uuid = uuid.UUID(patient_id)
        print(f"Valid UUID: {patient_uuid}")
    except ValueError:
        print(f"Invalid UUID: {patient_id}")
        return
    
    # Check in old system (diet_planner.Patient)
    print("\n=== Checking Old System (diet_planner.Patient) ===")
    try:
        patient = Patient.objects.get(id=patient_uuid)
        print(f"✓ Found patient in old system: {patient.name}")
        print(f"  - Dietitian: {patient.dietitian.username}")
        print(f"  - User Profile: {patient.user_profile}")
        print(f"  - Age: {patient.age}")
        print(f"  - Gender: {patient.gender}")
        return True
    except Patient.DoesNotExist:
        print("✗ Patient not found in old system")
    except Exception as e:
        print(f"✗ Error checking old system: {e}")
    
    # Check in new system (user_management.UserProfile)
    print("\n=== Checking New System (user_management.UserProfile) ===")
    try:
        user_profile = UserProfile.objects.get(id=patient_uuid, user_type='patient')
        print(f"✓ Found user profile: {user_profile.user.get_full_name()}")
        print(f"  - User: {user_profile.user.username}")
        print(f"  - Email: {user_profile.user.email}")
        
        # Check for patient profile
        try:
            patient_profile = PatientProfile.objects.get(user_profile=user_profile)
            print(f"  - Patient Profile: ✓ Found")
            print(f"  - Assigned Doctor: {patient_profile.assigned_doctor}")
            print(f"  - Age: {patient_profile.age}")
            print(f"  - Gender: {patient_profile.gender}")
            return True
        except PatientProfile.DoesNotExist:
            print("  - Patient Profile: ✗ Not found")
            
    except UserProfile.DoesNotExist:
        print("✗ User profile not found in new system")
    except Exception as e:
        print(f"✗ Error checking new system: {e}")
    
    return False

if __name__ == "__main__":
    patient_id = "b13e11b2-f159-4e4e-b17b-e64fc40a9303"
    found = check_patient(patient_id)
    
    if not found:
        print("\n=== Listing All Patients ===")
        print("Old System Patients:")
        for patient in Patient.objects.all():
            print(f"  - {patient.id}: {patient.name} (Dietitian: {patient.dietitian.username})")
        
        print("\nNew System Patient Profiles:")
        for profile in UserProfile.objects.filter(user_type='patient'):
            print(f"  - {profile.id}: {profile.user.get_full_name()}")
