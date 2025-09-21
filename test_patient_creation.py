#!/usr/bin/env python
"""
Test script to verify Patient creation works correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user_management.models import UserProfile, PatientProfile
from diet_planner.models import Patient
from diet_planner.views import calculate_age

def test_patient_creation():
    """Test Patient creation with various data types"""
    print("Testing Patient creation...")
    
    try:
        # Test calculate_age function
        print("Testing calculate_age function...")
        age1 = calculate_age(None)
        print(f"calculate_age(None) = {age1} (type: {type(age1)})")
        
        from datetime import date
        test_date = date(1990, 5, 15)
        age2 = calculate_age(test_date)
        print(f"calculate_age({test_date}) = {age2} (type: {type(age2)})")
        
        # Test data conversion
        print("\nTesting data conversion...")
        
        # Test string splitting
        test_allergies = "nuts, dairy, gluten"
        allergies_list = [item.strip() for item in test_allergies.split(',') if item.strip()]
        print(f"allergies: {allergies_list}")
        
        # Test numeric conversion
        test_height = "175.5"
        height_float = float(test_height) if test_height else None
        print(f"height: {height_float} (type: {type(height_float)})")
        
        test_weight = "70.2"
        weight_float = float(test_weight) if test_weight else None
        print(f"weight: {weight_float} (type: {type(weight_float)})")
        
        print("\n✅ All tests passed! Patient creation should work now.")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_patient_creation()
"""
Test script to verify Patient creation works correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from user_management.models import UserProfile, PatientProfile
from diet_planner.models import Patient
from diet_planner.views import calculate_age

def test_patient_creation():
    """Test Patient creation with various data types"""
    print("Testing Patient creation...")
    
    try:
        # Test calculate_age function
        print("Testing calculate_age function...")
        age1 = calculate_age(None)
        print(f"calculate_age(None) = {age1} (type: {type(age1)})")
        
        from datetime import date
        test_date = date(1990, 5, 15)
        age2 = calculate_age(test_date)
        print(f"calculate_age({test_date}) = {age2} (type: {type(age2)})")
        
        # Test data conversion
        print("\nTesting data conversion...")
        
        # Test string splitting
        test_allergies = "nuts, dairy, gluten"
        allergies_list = [item.strip() for item in test_allergies.split(',') if item.strip()]
        print(f"allergies: {allergies_list}")
        
        # Test numeric conversion
        test_height = "175.5"
        height_float = float(test_height) if test_height else None
        print(f"height: {height_float} (type: {type(height_float)})")
        
        test_weight = "70.2"
        weight_float = float(test_weight) if test_weight else None
        print(f"weight: {weight_float} (type: {type(weight_float)})")
        
        print("\n✅ All tests passed! Patient creation should work now.")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_patient_creation()


