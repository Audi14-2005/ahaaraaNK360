from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import json


class Patient(models.Model):
    """Patient profile for diet planning"""
    PRAKRITI_CHOICES = [
        ('vata', 'Vata'),
        ('pitta', 'Pitta'),
        ('kapha', 'Kapha'),
        ('vata_pitta', 'Vata-Pitta'),
        ('vata_kapha', 'Vata-Kapha'),
        ('pitta_kapha', 'Pitta-Kapha'),
        ('tridosha', 'Tridosha (Balanced)'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Lightly active (light exercise 1-3 days/week)'),
        ('moderate', 'Moderately active (moderate exercise 3-5 days/week)'),
        ('active', 'Very active (hard exercise 6-7 days/week)'),
        ('very_active', 'Extremely active (very hard exercise, physical job)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dietitian = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patients')
    user_profile = models.ForeignKey('user_management.UserProfile', on_delete=models.CASCADE, related_name='diet_patient', null=True, blank=True)
    
    # Basic Information
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(120)])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other')
    height = models.FloatField(blank=True, null=True, help_text="Height in cm")
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kg")
    
    # Ayurvedic Profile
    prakriti = models.CharField(max_length=20, choices=PRAKRITI_CHOICES, default='tridoshic')
    vikriti = models.CharField(max_length=20, choices=PRAKRITI_CHOICES, blank=True, null=True)
    
    # Lifestyle
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='sedentary')
    occupation = models.CharField(max_length=100, blank=True)
    
    # Health Information
    allergies = models.JSONField(default=list, blank=True)
    medical_conditions = models.JSONField(default=list, blank=True)
    medications = models.JSONField(default=list, blank=True)
    
    # Dietary Preferences
    dietary_preferences = models.JSONField(default=list, blank=True)
    food_dislikes = models.JSONField(default=list, blank=True)
    
    # Goals
    primary_goal = models.CharField(max_length=100, default="general_wellness")
    target_weight = models.FloatField(null=True, blank=True)
    
    # Calculated Fields
    bmi = models.FloatField(null=True, blank=True)
    daily_calorie_needs = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_prakriti_display()}"
    
    def save(self, *args, **kwargs):
        # Calculate BMI
        if self.height and self.weight:
            self.bmi = round(self.weight / ((self.height / 100) ** 2), 2)
        
        # Calculate daily calorie needs
        if self.age and self.height and self.weight and self.gender and self.activity_level:
            self.daily_calorie_needs = self.calculate_daily_calories()
        
        super().save(*args, **kwargs)
    
    def calculate_daily_calories(self):
        """Calculate daily calorie needs using Harris-Benedict formula"""
        if self.gender == 'male':
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            bmr = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)
        
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        multiplier = activity_multipliers.get(self.activity_level, 1.2)
        return int(bmr * multiplier)
    
    def get_bmi(self):
        """Calculate BMI value"""
        if self.height and self.weight and self.height > 0 and self.weight > 0:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 2)
        return 0.0
    
    def get_daily_calorie_needs(self):
        """Calculate daily calorie needs using TDEE"""
        if not self.height or not self.weight or not self.age:
            return 2000  # Default calorie needs
        
        bmr = self.get_basal_metabolic_rate()
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        multiplier = activity_multipliers.get(self.activity_level, 1.2)
        return int(bmr * multiplier)
    
    def get_basal_metabolic_rate(self):
        """Calculate BMR using Harris-Benedict Equation"""
        if not self.height or not self.weight or not self.age:
            return 1500  # Default BMR
        
        if self.gender == 'male':
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        elif self.gender == 'female':
            bmr = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)
        else:  # For 'other' or unspecified, use male formula as fallback
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        return bmr


class Food(models.Model):
    """Food database with Ayurvedic properties"""
    PRAKRITI_EFFECT_CHOICES = [
        ('pacifies', 'Pacifies'),
        ('aggravates', 'Aggravates'),
        ('neutral', 'Neutral'),
    ]
    
    TASTE_CHOICES = [
        ('sweet', 'Sweet'),
        ('sour', 'Sour'),
        ('salty', 'Salty'),
        ('pungent', 'Pungent'),
        ('bitter', 'Bitter'),
        ('astringent', 'Astringent'),
    ]
    
    ENERGY_CHOICES = [
        ('cooling', 'Cooling'),
        ('heating', 'Heating'),
        ('neutral', 'Neutral'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    
    # Nutritional Information (per 100g)
    calories = models.PositiveIntegerField()
    protein = models.FloatField()
    carbohydrates = models.FloatField()
    fat = models.FloatField()
    fiber = models.FloatField()
    
    # Ayurvedic Properties
    primary_taste = models.CharField(max_length=20, choices=TASTE_CHOICES)
    secondary_taste = models.CharField(max_length=20, choices=TASTE_CHOICES, blank=True, null=True)
    energy = models.CharField(max_length=20, choices=ENERGY_CHOICES)
    
    # Dosha Effects
    vata_effect = models.CharField(max_length=20, choices=PRAKRITI_EFFECT_CHOICES)
    pitta_effect = models.CharField(max_length=20, choices=PRAKRITI_EFFECT_CHOICES)
    kapha_effect = models.CharField(max_length=20, choices=PRAKRITI_EFFECT_CHOICES)
    
    # Dietary Properties
    is_vegetarian = models.BooleanField(default=True)
    is_vegan = models.BooleanField(default=True)
    is_gluten_free = models.BooleanField(default=True)
    is_dairy_free = models.BooleanField(default=True)
    
    # Allergens
    contains_nuts = models.BooleanField(default=False)
    contains_soy = models.BooleanField(default=False)
    contains_eggs = models.BooleanField(default=False)
    contains_fish = models.BooleanField(default=False)
    contains_shellfish = models.BooleanField(default=False)
    
    # AI Vector Embedding
    vector_embedding = models.JSONField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DietChart(models.Model):
    """Diet chart generated for a patient"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diet_charts')
    dietitian = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diet_charts')
    
    # Chart Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # AI Generation Info
    generated_by_ai = models.BooleanField(default=True)
    ai_model_used = models.CharField(max_length=100, default='rule_based_architect')
    generation_notes = models.TextField(blank=True)
    
    # Chart Settings
    duration_days = models.PositiveIntegerField(default=7)
    meals_per_day = models.PositiveIntegerField(default=3)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.patient.name}"


class MealPlan(models.Model):
    """Individual meal plan within a diet chart"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('pre_workout', 'Pre-Workout'),
        ('post_workout', 'Post-Workout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diet_chart = models.ForeignKey(DietChart, on_delete=models.CASCADE, related_name='meal_plans')
    
    # Meal Information
    day_number = models.PositiveIntegerField(help_text="Day of the week (1-7)")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    meal_time = models.TimeField(help_text="Recommended time for this meal")
    
    # Nutritional Targets
    target_calories = models.PositiveIntegerField()
    target_protein = models.FloatField()
    target_carbs = models.FloatField()
    target_fat = models.FloatField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day_number', 'meal_time']
        unique_together = ['diet_chart', 'day_number', 'meal_type']
    
    def __str__(self):
        return f"Day {self.day_number} - {self.get_meal_type_display()}"


class MealItem(models.Model):
    """Individual food item within a meal plan"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='meal_items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    
    # Quantity Information
    quantity = models.FloatField(help_text="Quantity in grams")
    serving_size = models.CharField(max_length=50, help_text="e.g., '1 cup', '2 pieces'")
    
    # Calculated Nutritional Values
    calories = models.PositiveIntegerField()
    protein = models.FloatField()
    carbohydrates = models.FloatField()
    fat = models.FloatField()
    fiber = models.FloatField()
    
    # AI Generation Info
    is_ai_generated = models.BooleanField(default=True)
    ai_confidence_score = models.FloatField(null=True, blank=True)
    
    # Swapping History
    original_food = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='swapped_versions')
    swap_reason = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.food.name} - {self.quantity}g"
    
    def save(self, *args, **kwargs):
        # Calculate nutritional values based on quantity
        if self.food and self.quantity:
            multiplier = self.quantity / 100  # Convert to per-100g basis
            self.calories = int(self.food.calories * multiplier)
            self.protein = round(self.food.protein * multiplier, 2)
            self.carbohydrates = round(self.food.carbohydrates * multiplier, 2)
            self.fat = round(self.food.fat * multiplier, 2)
            self.fiber = round(self.food.fiber * multiplier, 2)
        
        super().save(*args, **kwargs)


class FoodSwapLog(models.Model):
    """Log of food swaps made using AI #2 (The Specialist)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meal_item = models.ForeignKey(MealItem, on_delete=models.CASCADE, related_name='swap_logs')
    dietitian = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Swap Information
    original_food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='original_swaps')
    new_food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='new_swaps')
    swap_reason = models.TextField(blank=True)
    
    # AI Analysis
    similarity_score = models.FloatField()
    ai_model_used = models.CharField(max_length=100, default='vector_similarity_specialist')
    alternative_suggestions = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_food.name} → {self.new_food.name}"


class Recipe(models.Model):
    """Recipe for food preparation with Ayurvedic guidelines"""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    COOKING_TIME_CHOICES = [
        ('quick', 'Quick (0-15 min)'),
        ('moderate', 'Moderate (15-30 min)'),
        ('long', 'Long (30+ min)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    name = models.CharField(max_length=200)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='recipes')
    description = models.TextField(blank=True, help_text="Brief description of the recipe")
    
    # Recipe Details
    ingredients = models.JSONField(default=list, help_text="List of ingredients with quantities")
    instructions = models.JSONField(default=list, help_text="Step-by-step cooking instructions")
    cooking_time = models.CharField(max_length=20, choices=COOKING_TIME_CHOICES, default='moderate')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    servings = models.PositiveIntegerField(default=1, help_text="Number of servings")
    
    # Nutritional Information (per serving)
    calories_per_serving = models.FloatField(default=0.0)
    protein_per_serving = models.FloatField(default=0.0)
    carbs_per_serving = models.FloatField(default=0.0)
    fat_per_serving = models.FloatField(default=0.0)
    
    # Ayurvedic Guidelines
    ayurvedic_benefits = models.TextField(blank=True, help_text="Ayurvedic benefits of this preparation")
    best_time_to_eat = models.CharField(max_length=100, blank=True, help_text="Best time to consume (e.g., 'Morning', 'Evening')")
    seasonal_notes = models.TextField(blank=True, help_text="Seasonal considerations")
    dosha_considerations = models.TextField(blank=True, help_text="Special notes for different doshas")
    
    # Tips and Variations
    cooking_tips = models.TextField(blank=True, help_text="Helpful cooking tips")
    variations = models.TextField(blank=True, help_text="Alternative preparation methods")
    storage_instructions = models.TextField(blank=True, help_text="How to store leftovers")
    
    # Media
    image = models.ImageField(upload_to='recipe_images/', blank=True, null=True)
    video_url = models.URLField(blank=True, help_text="Optional video tutorial URL")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_recipes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True, help_text="Can be viewed by patients")
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'food']
    
    def __str__(self):
        return f"{self.name} - {self.food.name}"
    
    def get_total_cooking_time(self):
        """Get estimated total cooking time in minutes"""
        time_mapping = {
            'quick': 10,
            'moderate': 22,
            'long': 45,
        }
        return time_mapping.get(self.cooking_time, 22)
    
    def get_ingredients_list(self):
        """Get formatted ingredients list"""
        if isinstance(self.ingredients, list):
            return self.ingredients
        return []
    
    def get_instructions_list(self):
        """Get formatted instructions list"""
        if isinstance(self.instructions, list):
            return self.instructions
        return []