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

def test_specific_patient():
    patient_id = "b13e11b2-f159-4e4e-b17b-e64fc40a9303"
    print(f"Testing patient ID: {patient_id}")
    
    try:
        patient_uuid = uuid.UUID(patient_id)
        print(f"✓ Valid UUID: {patient_uuid}")
    except ValueError:
        print(f"✗ Invalid UUID: {patient_id}")
        return
    
    # Check in old system
    print("\n=== Old System Check ===")
    try:
        patient = Patient.objects.get(id=patient_uuid)
        print(f"✓ Found patient: {patient.name}")
        print(f"  - Dietitian: {patient.dietitian.username}")
        print(f"  - User Profile: {patient.user_profile}")
        print(f"  - Age: {patient.age}")
        print(f"  - Gender: {patient.gender}")
        
        # Check if patient belongs to current user
        current_user = User.objects.get(username='Kabi12211')  # From the logs
        print(f"  - Current user: {current_user.username}")
        print(f"  - Patient belongs to current user: {patient.dietitian == current_user}")
        
    except Patient.DoesNotExist:
        print("✗ Patient not found in old system")
    except User.DoesNotExist:
        print("✗ Current user not found")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Check in new system
    print("\n=== New System Check ===")
    try:
        user_profile = UserProfile.objects.get(id=patient_uuid, user_type='patient')
        print(f"✓ Found user profile: {user_profile.user.get_full_name()}")
        print(f"  - User: {user_profile.user.username}")
        print(f"  - Email: {user_profile.user.email}")
        
        try:
            patient_profile = PatientProfile.objects.get(user_profile=user_profile)
            print(f"  - Patient Profile: ✓ Found")
            print(f"  - Assigned Doctor: {patient_profile.assigned_doctor}")
        except PatientProfile.DoesNotExist:
            print("  - Patient Profile: ✗ Not found")
            
    except UserProfile.DoesNotExist:
        print("✗ User profile not found in new system")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # List all patients for current user
    print("\n=== All Patients for Current User ===")
    try:
        current_user = User.objects.get(username='Kabi12211')
        patients = Patient.objects.filter(dietitian=current_user)
        print(f"Found {patients.count()} patients for {current_user.username}:")
        for patient in patients:
            print(f"  - {patient.id}: {patient.name}")
    except User.DoesNotExist:
        print("Current user not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_specific_patient()
