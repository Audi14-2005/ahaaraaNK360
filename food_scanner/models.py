"""
Food Scanner Models
AI-powered food analysis and nutritional information
"""
import uuid
from django.db import models
from django.contrib.auth.models import User


class FoodScan(models.Model):
    """Represents a food scan/analysis session"""
    
    SCAN_TYPES = [
        ('camera', 'Camera Scan'),
        ('upload', 'File Upload'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_scans')
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPES)
    image = models.ImageField(upload_to='food_scans/')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # AI Analysis Results
    detected_food = models.CharField(max_length=200, blank=True)
    confidence_score = models.FloatField(default=0.0)
    
    # Nutritional Information (per 100g)
    calories = models.FloatField(default=0.0)
    protein = models.FloatField(default=0.0)
    carbohydrates = models.FloatField(default=0.0)
    fat = models.FloatField(default=0.0)
    fiber = models.FloatField(default=0.0)
    sugar = models.FloatField(default=0.0)
    
    # Ayurvedic Properties
    rasa = models.CharField(max_length=50, blank=True)  # Taste
    virya = models.CharField(max_length=50, blank=True)  # Energy
    vipaka = models.CharField(max_length=50, blank=True)  # Post-digestive effect
    guna = models.CharField(max_length=100, blank=True)  # Qualities
    
    # Dosha Effects
    VATA_CHOICES = [
        ('pacifies', 'Pacifies'),
        ('aggravates', 'Aggravates'),
        ('neutral', 'Neutral'),
        ('moderate', 'Moderate'),
        ('avoid', 'Avoid'),
    ]
    
    PITTA_CHOICES = [
        ('pacifies', 'Pacifies'),
        ('aggravates', 'Aggravates'),
        ('neutral', 'Neutral'),
        ('moderate', 'Moderate'),
        ('avoid', 'Avoid'),
    ]
    
    KAPHA_CHOICES = [
        ('pacifies', 'Pacifies'),
        ('aggravates', 'Aggravates'),
        ('neutral', 'Neutral'),
        ('moderate', 'Moderate'),
        ('avoid', 'Avoid'),
    ]
    
    vata_effect = models.CharField(max_length=20, choices=VATA_CHOICES, default='neutral')
    pitta_effect = models.CharField(max_length=20, choices=PITTA_CHOICES, default='neutral')
    kapha_effect = models.CharField(max_length=20, choices=KAPHA_CHOICES, default='neutral')
    
    # Additional Analysis
    ayurvedic_description = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    warnings = models.TextField(blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Food Scan - {self.detected_food or 'Unknown'} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_nutritional_summary(self):
        """Get a summary of nutritional information"""
        return {
            'calories': self.calories,
            'protein': self.protein,
            'carbohydrates': self.carbohydrates,
            'fat': self.fat,
            'fiber': self.fiber,
            'sugar': self.sugar,
        }
    
    def get_ayurvedic_summary(self):
        """Get a summary of Ayurvedic properties"""
        return {
            'rasa': self.rasa,
            'virya': self.virya,
            'vipaka': self.vipaka,
            'guna': self.guna,
            'vata_effect': self.get_vata_effect_display(),
            'pitta_effect': self.get_pitta_effect_display(),
            'kapha_effect': self.get_kapha_effect_display(),
        }


class FoodDatabase(models.Model):
    """Database of known foods for AI training and reference"""
    
    CATEGORIES = [
        ('fruits', 'Fruits'),
        ('vegetables', 'Vegetables'),
        ('grains', 'Grains'),
        ('proteins', 'Proteins'),
        ('dairy', 'Dairy'),
        ('spices', 'Spices'),
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks'),
        ('desserts', 'Desserts'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORIES, blank=True)
    image = models.ImageField(upload_to='food_database/', blank=True, null=True)
    
    # Additional CSV fields
    meal_type = models.CharField(max_length=50, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    
    # Nutritional Information (per 100g)
    calories = models.FloatField(default=0.0)
    protein = models.FloatField(default=0.0)
    carbohydrates = models.FloatField(default=0.0)
    fat = models.FloatField(default=0.0)
    fiber = models.FloatField(default=0.0)
    sugar = models.FloatField(default=0.0)
    
    # Ayurvedic Properties
    primary_taste = models.CharField(max_length=50, blank=True)  # Rasa
    energy = models.CharField(max_length=50, blank=True)  # Virya
    vipaka = models.CharField(max_length=50, blank=True)
    guna = models.CharField(max_length=100, blank=True)
    
    # Dosha Effects
    vata_effect = models.CharField(max_length=20, choices=FoodScan.VATA_CHOICES, default='neutral')
    pitta_effect = models.CharField(max_length=20, choices=FoodScan.PITTA_CHOICES, default='neutral')
    kapha_effect = models.CharField(max_length=20, choices=FoodScan.KAPHA_CHOICES, default='neutral')
    
    # Additional Information
    recommendations = models.TextField(blank=True)
    avoidances = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name