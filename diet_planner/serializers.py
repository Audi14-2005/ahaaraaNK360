from rest_framework import serializers
from .models import Patient, Food, DietChart, MealPlan, MealItem, Recipe
from user_management.models import UserProfile, PatientProfile


class FoodSerializer(serializers.ModelSerializer):
    """Serializer for Food model"""
    
    class Meta:
        model = Food
        fields = [
            'id', 'name', 'category', 'subcategory', 'primary_taste', 
            'secondary_taste', 'energy_kcal', 'protein_g', 'carbs_g', 
            'fat_g', 'fiber_g', 'vitamins', 'minerals', 'benefits', 
            'contraindications', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'food', 'description', 'ingredients', 
            'instructions', 'cooking_time', 'difficulty', 'servings', 
            'nutritional_info', 'video_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model"""
    
    class Meta:
        model = Patient
        fields = [
            'id', 'name', 'age', 'gender', 'height', 'weight', 
            'prakriti', 'activity_level', 'occupation', 'allergies', 
            'medical_conditions', 'dietary_preferences', 'primary_goal', 
            'target_weight', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MealItemSerializer(serializers.ModelSerializer):
    """Serializer for MealItem model"""
    food = FoodSerializer(read_only=True)
    food_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = MealItem
        fields = [
            'id', 'food', 'food_id', 'quantity', 'unit', 'notes', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MealPlanSerializer(serializers.ModelSerializer):
    """Serializer for MealPlan model"""
    meal_items = MealItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = MealPlan
        fields = [
            'id', 'diet_chart', 'day_number', 'meal_time', 'meal_items', 
            'total_calories', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DietChartSerializer(serializers.ModelSerializer):
    """Serializer for DietChart model"""
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.UUIDField(write_only=True)
    meal_plans = MealPlanSerializer(many=True, read_only=True)
    
    class Meta:
        model = DietChart
        fields = [
            'id', 'patient', 'patient_id', 'title', 'description', 
            'duration_days', 'start_date', 'end_date', 'status', 
            'meal_plans', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    
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
