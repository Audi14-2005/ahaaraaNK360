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
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from diet_planner.views import patient_list, patient_detail, generate_diet_chart, calculate_age
import uuid

def test_all_functionality():
    print("=== Testing All Patient Functionality ===")
    
    # Test calculate_age function
    print("\n1. Testing calculate_age function...")
    from datetime import date
    test_date = date(1990, 1, 1)
    age = calculate_age(test_date)
    expected_age = date.today().year - 1990
    print(f"   Age calculation: {age} years (expected: {expected_age})")
    if age == expected_age:
        print("   ✓ calculate_age function working correctly")
    else:
        print("   ✗ calculate_age function failed")
    
    # Test with None
    age_none = calculate_age(None)
    print(f"   Age with None: {age_none}")
    if age_none == 'Not set':
        print("   ✓ calculate_age handles None correctly")
    else:
        print("   ✗ calculate_age failed to handle None")
    
    # Test patient list view
    print("\n2. Testing patient list view...")
    try:
        # Get a dietitian user
        dietitian_users = User.objects.filter(profile__user_type='dietitian')
        if dietitian_users.exists():
            user = dietitian_users.first()
            print(f"   Testing with dietitian: {user.username}")
            
            # Create a mock request
            factory = RequestFactory()
            request = factory.get('/diet-planner/patients/')
            request.user = user
            
            # Test the view
            response = patient_list(request)
            print(f"   Patient list view status: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ Patient list view working correctly")
            else:
                print(f"   ✗ Patient list view failed with status {response.status_code}")
        else:
            print("   No dietitian users found")
            
    except Exception as e:
        print(f"   ✗ Error testing patient list view: {e}")
    
    # Test patient detail view
    print("\n3. Testing patient detail view...")
    try:
        # Get a patient ID to test with
        patients = Patient.objects.all()
        if patients.exists():
            patient = patients.first()
            print(f"   Testing with patient: {patient.name} (ID: {patient.id})")
            
            # Create a mock request
            factory = RequestFactory()
            request = factory.get(f'/diet-planner/patients/{patient.id}/')
            request.user = patient.dietitian
            
            # Test the view
            response = patient_detail(request, patient.id)
            print(f"   Patient detail view status: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ Patient detail view working correctly")
            else:
                print(f"   ✗ Patient detail view failed with status {response.status_code}")
        else:
            print("   No patients found")
            
    except Exception as e:
        print(f"   ✗ Error testing patient detail view: {e}")
    
    # Test generate diet chart view
    print("\n4. Testing generate diet chart view...")
    try:
        # Get a patient ID to test with
        patients = Patient.objects.all()
        if patients.exists():
            patient = patients.first()
            print(f"   Testing with patient: {patient.name} (ID: {patient.id})")
            
            # Create a mock request
            factory = RequestFactory()
            request = factory.get(f'/diet-planner/patients/{patient.id}/generate-chart/')
            request.user = patient.dietitian
            
            # Test the view
            response = generate_diet_chart(request, patient.id)
            print(f"   Generate diet chart view status: {response.status_code}")
            if response.status_code in [200, 302]:  # 302 is redirect, which is also OK
                print("   ✓ Generate diet chart view working correctly")
            else:
                print(f"   ✗ Generate diet chart view failed with status {response.status_code}")
        else:
            print("   No patients found")
            
    except Exception as e:
        print(f"   ✗ Error testing generate diet chart view: {e}")
    
    # Test specific problematic patient ID
    print("\n5. Testing specific patient ID...")
    problematic_id = "b13e11b2-f159-4e4e-b17b-e64fc40a9303"
    try:
        patient_uuid = uuid.UUID(problematic_id)
        print(f"   Testing patient ID: {problematic_id}")
        
        # Check if patient exists
        patient_exists = Patient.objects.filter(id=patient_uuid).exists()
        print(f"   Patient exists in old system: {patient_exists}")
        
        if patient_exists:
            patient = Patient.objects.get(id=patient_uuid)
            print(f"   Patient found: {patient.name}")
            print(f"   Dietitian: {patient.dietitian.username}")
            
            # Test with the correct dietitian
            factory = RequestFactory()
            request = factory.get(f'/diet-planner/patients/{patient.id}/')
            request.user = patient.dietitian
            
            response = patient_detail(request, patient.id)
            print(f"   Patient detail status: {response.status_code}")
            if response.status_code == 200:
                print("   ✓ Specific patient ID working correctly")
            else:
                print(f"   ✗ Specific patient ID failed with status {response.status_code}")
        else:
            print("   Patient not found in old system")
            
    except ValueError:
        print(f"   ✗ Invalid UUID: {problematic_id}")
    except Exception as e:
        print(f"   ✗ Error testing specific patient: {e}")
    
    # Database summary
    print("\n6. Database Summary:")
    print(f"   Total patients (old system): {Patient.objects.count()}")
    print(f"   Total user profiles: {UserProfile.objects.count()}")
    print(f"   Total patient profiles: {PatientProfile.objects.count()}")
    
    print("\n=== Test Completed ===")

if __name__ == "__main__":
    test_all_functionality()
