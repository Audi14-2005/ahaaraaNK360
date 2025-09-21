from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, PatientProfile, DietitianProfile, PrakritiResponse, DiseaseResponse


class UserRegistrationForm(UserCreationForm):
    """User registration form with user type selection"""
    
    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('dietitian', 'Dietitian'),
    ]
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type', 'phone_number')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create user profile
            user_profile = UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                phone_number=self.cleaned_data['phone_number']
            )
            
            # Create specific profile based on user type
            if self.cleaned_data['user_type'] == 'patient':
                PatientProfile.objects.create(user_profile=user_profile)
            elif self.cleaned_data['user_type'] == 'dietitian':
                DietitianProfile.objects.create(user_profile=user_profile)
        
        return user


class PatientProfileForm(forms.ModelForm):
    """Form for updating patient profile"""
    
    class Meta:
        model = PatientProfile
        fields = [
            'gender', 'height', 'weight', 'blood_group',
            'emergency_contact_name', 'emergency_contact_phone',
            'medical_conditions', 'allergies', 'current_medications'
        ]
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'current_medications': forms.Textarea(attrs={'rows': 3}),
        }


class DietitianProfileForm(forms.ModelForm):
    """Form for updating dietitian profile"""
    
    class Meta:
        model = DietitianProfile
        fields = [
            'qualification', 'license_number', 'specialization',
            'experience_years', 'bio', 'clinic_name', 'clinic_address',
            'consultation_fee', 'is_available', 'consultation_hours'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'clinic_address': forms.Textarea(attrs={'rows': 3}),
            'consultation_hours': forms.Textarea(attrs={'rows': 2}),
        }


class AppointmentForm(forms.Form):
    """Form for booking appointments"""
    
    APPOINTMENT_TYPE_CHOICES = [
        ('in_person', 'In-Person Consultation'),
        ('virtual', 'Virtual Consultation'),
    ]
    
    dietitian = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(user_type='dietitian'),
        empty_label="Select a Dietitian",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    appointment_type = forms.ChoiceField(
        choices=APPOINTMENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    reason_for_visit = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        help_text="Please describe the reason for your consultation"
    )
    duration_minutes = forms.IntegerField(
        initial=60,
        min_value=15,
        max_value=180,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Duration in minutes"
    )
    consultation_fee = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=100.00,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        help_text="Consultation fee in USD"
    )


class PrakritiResponseForm(forms.Form):
    """Form for Prakriti analysis responses"""
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        
        # Create choice field for options
        choices = [(option.id, option.option_text) for option in question.options.all()]
        self.fields['selected_option'] = forms.ChoiceField(
            choices=choices,
            widget=forms.RadioSelect,
            label=question.question_text
        )


class DiseaseResponseForm(forms.Form):
    """Form for disease analysis responses"""
    
    RESPONSE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('sometimes', 'Sometimes'),
        ('not_sure', 'Not Sure'),
    ]
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        
        self.fields['response'] = forms.ChoiceField(
            choices=self.RESPONSE_CHOICES,
            widget=forms.RadioSelect,
            label=question.question_text
        )
        self.fields['notes'] = forms.CharField(
            widget=forms.Textarea(attrs={'rows': 2}),
            required=False,
            help_text="Additional notes (optional)"
        )


class VirtualMeetingForm(forms.Form):
    """Form for virtual meeting details"""
    
    meeting_platform = forms.ChoiceField(
        choices=[
            ('zoom', 'Zoom'),
            ('google_meet', 'Google Meet'),
            ('teams', 'Microsoft Teams'),
            ('other', 'Other'),
        ]
    )
    meeting_link = forms.URLField(required=False)
    meeting_id = forms.CharField(max_length=100, required=False)
    meeting_password = forms.CharField(max_length=50, required=False)
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Additional meeting instructions"
    )
