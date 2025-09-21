from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, PatientProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_type', 'phone_number', 'date_of_birth', 
            'address', 'city', 'state', 'country', 'postal_code', 
            'profile_picture', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for PatientProfile model"""
    user_profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user_profile', 'assigned_doctor', 'height', 'weight', 
            'blood_type', 'allergies', 'medical_conditions', 
            'current_medications', 'emergency_contact_name', 
            'emergency_contact_phone', 'gender', 'dominant_dosha', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
