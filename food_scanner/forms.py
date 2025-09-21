"""
Food Scanner Forms
"""
from django import forms
from .models import FoodScan, FoodDatabase


class FoodScanForm(forms.ModelForm):
    """Form for food scanning"""
    
    class Meta:
        model = FoodScan
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'imageInput',
                'accept': 'image/*',
                'capture': 'environment'  # For mobile camera
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True


class FoodDatabaseForm(forms.ModelForm):
    """Form for adding foods to the database"""
    
    class Meta:
        model = FoodDatabase
        fields = [
            'name', 'category', 'image', 'meal_type', 'tags', 'calories', 'protein', 'carbohydrates',
            'fat', 'fiber', 'sugar', 'primary_taste', 'energy', 'vipaka', 'guna',
            'vata_effect', 'pitta_effect', 'kapha_effect', 'recommendations', 'avoidances'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter food name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '0.0'
            }),
            'protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '0.0'
            }),
            'carbohydrates': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '0.0'
            }),
            'fat': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '0.0'
            }),
            'fiber': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '0.0'
            }),
            'sugar': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '0.0'
            }),
            'primary_taste': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., sweet, sour, salty'
            }),
            'energy': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., heating, cooling, neutral'
            }),
            'vipaka': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., sweet, sour, pungent'
            }),
            'guna': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., light, heavy, dry, oily'
            }),
            'vata_effect': forms.Select(attrs={
                'class': 'form-select'
            }),
            'pitta_effect': forms.Select(attrs={
                'class': 'form-select'
            }),
            'kapha_effect': forms.Select(attrs={
                'class': 'form-select'
            }),
            'meal_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Breakfast, Lunch, Dinner, Snack'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., healthy, organic, spicy'
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'General recommendations for this food'
            }),
            'avoidances': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Warnings or avoidances for this food'
            }),
        }
