from django.contrib import admin
from .models import Patient, Food, DietChart, MealPlan, MealItem, FoodSwapLog


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'prakriti', 'age', 'gender', 'bmi', 'daily_calorie_needs', 'dietitian', 'created_at']
    list_filter = ['prakriti', 'gender', 'activity_level', 'dietitian', 'created_at']
    search_fields = ['name', 'occupation']
    readonly_fields = ['bmi', 'daily_calorie_needs', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('dietitian', 'name', 'age', 'gender', 'height', 'weight')
        }),
        ('Ayurvedic Profile', {
            'fields': ('prakriti', 'vikriti')
        }),
        ('Lifestyle', {
            'fields': ('activity_level', 'occupation')
        }),
        ('Health Information', {
            'fields': ('allergies', 'medical_conditions', 'medications')
        }),
        ('Dietary Preferences', {
            'fields': ('dietary_preferences', 'food_dislikes')
        }),
        ('Goals', {
            'fields': ('primary_goal', 'target_weight')
        }),
        ('Calculated Fields', {
            'fields': ('bmi', 'daily_calorie_needs'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories', 'primary_taste', 'energy', 'vata_effect', 'pitta_effect', 'kapha_effect']
    list_filter = ['category', 'primary_taste', 'energy', 'vata_effect', 'pitta_effect', 'kapha_effect', 'is_vegetarian', 'is_vegan']
    search_fields = ['name', 'category', 'subcategory']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'subcategory')
        }),
        ('Nutritional Information (per 100g)', {
            'fields': ('calories', 'protein', 'carbohydrates', 'fat', 'fiber')
        }),
        ('Ayurvedic Properties', {
            'fields': ('primary_taste', 'secondary_taste', 'energy')
        }),
        ('Dosha Effects', {
            'fields': ('vata_effect', 'pitta_effect', 'kapha_effect')
        }),
        ('Dietary Properties', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_dairy_free')
        }),
        ('Allergens', {
            'fields': ('contains_nuts', 'contains_soy', 'contains_eggs', 'contains_fish', 'contains_shellfish')
        }),
        ('AI Features', {
            'fields': ('vector_embedding',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DietChart)
class DietChartAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'status', 'duration_days', 'generated_by_ai', 'ai_model_used', 'dietitian', 'created_at']
    list_filter = ['status', 'generated_by_ai', 'ai_model_used', 'dietitian', 'created_at']
    search_fields = ['title', 'patient__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Chart Information', {
            'fields': ('patient', 'dietitian', 'title', 'description', 'status')
        }),
        ('AI Generation', {
            'fields': ('generated_by_ai', 'ai_model_used', 'generation_notes')
        }),
        ('Settings', {
            'fields': ('duration_days', 'meals_per_day')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['diet_chart', 'day_number', 'meal_type', 'meal_time', 'target_calories']
    list_filter = ['meal_type', 'diet_chart__status', 'diet_chart__dietitian']
    search_fields = ['diet_chart__title', 'diet_chart__patient__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ['food', 'meal_plan', 'quantity', 'calories', 'is_ai_generated', 'ai_confidence_score']
    list_filter = ['is_ai_generated', 'food__category', 'meal_plan__meal_type']
    search_fields = ['food__name', 'meal_plan__diet_chart__title']
    readonly_fields = ['calories', 'protein', 'carbohydrates', 'fat', 'fiber', 'created_at', 'updated_at']


@admin.register(FoodSwapLog)
class FoodSwapLogAdmin(admin.ModelAdmin):
    list_display = ['original_food', 'new_food', 'similarity_score', 'ai_model_used', 'dietitian', 'created_at']
    list_filter = ['ai_model_used', 'dietitian', 'created_at']
    search_fields = ['original_food__name', 'new_food__name', 'meal_item__meal_plan__diet_chart__title']
    readonly_fields = ['created_at']