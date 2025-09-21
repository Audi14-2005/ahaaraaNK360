from django import forms
from .models import Patient, Food, DietChart

class PatientBasicInfoForm(forms.ModelForm):
    """Simplified form for updating basic patient information"""
    
    class Meta:
        model = Patient
        fields = ['age', 'height', 'weight']
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter age',
                'min': '1',
                'max': '120',
                'required': True
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height in cm',
                'min': '50',
                'max': '250',
                'step': '0.1',
                'required': True
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in kg',
                'min': '10',
                'max': '300',
                'step': '0.1',
                'required': True
            }),
        }
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 1 or age > 120):
            raise forms.ValidationError('Age must be between 1 and 120 years.')
        return age
    
    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height is not None and (height < 50 or height > 250):
            raise forms.ValidationError('Height must be between 50 and 250 cm.')
        return height
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and (weight < 10 or weight > 300):
            raise forms.ValidationError('Weight must be between 10 and 300 kg.')
        return weight

class PatientForm(forms.ModelForm):
    """Form for creating and editing patients"""
    
    class Meta:
        model = Patient
        fields = [
            'name', 'age', 'gender', 'height', 'weight', 
            'prakriti', 'activity_level', 'occupation', 
            'medical_conditions', 'allergies', 'dietary_preferences',
            'primary_goal', 'target_weight'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter age',
                'min': '1',
                'max': '120'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height in cm',
                'min': '50',
                'max': '250'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in kg',
                'min': '10',
                'max': '300'
            }),
            'prakriti': forms.Select(attrs={
                'class': 'form-select'
            }),
            'activity_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter occupation'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter medical conditions (comma-separated)',
                'rows': 3
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter allergies (comma-separated)',
                'rows': 3
            }),
            'dietary_preferences': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter dietary preferences (comma-separated)',
                'rows': 3
            }),
            'primary_goal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'target_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target weight in kg',
                'min': '10',
                'max': '300'
            }),
        }
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 1 or age > 120):
            raise forms.ValidationError('Age must be between 1 and 120 years.')
        return age
    
    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height is not None and (height < 50 or height > 250):
            raise forms.ValidationError('Height must be between 50 and 250 cm.')
        return height
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight is not None and (weight < 10 or weight > 300):
            raise forms.ValidationError('Weight must be between 10 and 300 kg.')
        return weight


class FoodForm(forms.ModelForm):
    """Form for creating and editing foods"""
    
    class Meta:
        model = Food
        fields = [
            'name', 'category', 'subcategory', 'primary_taste', 'secondary_taste',
            'calories', 'protein', 'carbohydrates', 'fat', 'fiber',
            'energy', 'vata_effect', 'pitta_effect', 'kapha_effect',
            'is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_dairy_free', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter food name'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category'
            }),
            'subcategory': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subcategory'
            }),
            'primary_taste': forms.Select(attrs={
                'class': 'form-select'
            }),
            'secondary_taste': forms.Select(attrs={
                'class': 'form-select'
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calories per 100g',
                'min': '0'
            }),
            'protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Protein per 100g',
                'step': '0.1',
                'min': '0'
            }),
            'carbohydrates': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Carbs per 100g',
                'step': '0.1',
                'min': '0'
            }),
            'fat': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fat per 100g',
                'step': '0.1',
                'min': '0'
            }),
            'fiber': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fiber per 100g',
                'step': '0.1',
                'min': '0'
            }),
            'energy': forms.Select(attrs={
                'class': 'form-select'
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
            'is_vegetarian': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_vegan': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_gluten_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_dairy_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name) < 2:
            raise forms.ValidationError('Food name must be at least 2 characters long.')
        return name
    
    def clean_calories(self):
        calories = self.cleaned_data.get('calories')
        if calories is not None and calories < 0:
            raise forms.ValidationError('Calories value cannot be negative.')
        return calories


class DietChartForm(forms.ModelForm):
    """Form for creating and editing diet charts"""
    
    class Meta:
        model = DietChart
        fields = ['title', 'description', 'duration_days']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter diet chart title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter description',
                'rows': 3
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of days',
                'min': '1',
                'max': '30'
            }),
        }