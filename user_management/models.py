from django.contrib.auth.models import User
from django.db import models
import uuid


class UserProfile(models.Model):
    """Extended user profile for both patients and dietitians"""
    
    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('dietitian', 'Dietitian'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_user_type_display()}"


class PatientProfile(models.Model):
    """Extended patient profile with medical information"""
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='patient_profile')
    
    # Doctor Assignment
    assigned_doctor = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name='assigned_patients', limit_choices_to={'user_type': 'dietitian'})
    
    # Basic Information
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    height = models.FloatField(help_text="Height in cm", null=True, blank=True)
    weight = models.FloatField(help_text="Weight in kg", null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    
    # Medical Information
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    medical_conditions = models.TextField(blank=True, help_text="List any medical conditions")
    allergies = models.TextField(blank=True, help_text="List any allergies")
    current_medications = models.TextField(blank=True, help_text="List current medications")
    
    # Analysis Results
    prakriti_analysis_completed = models.BooleanField(default=False)
    disease_analysis_completed = models.BooleanField(default=False)
    health_summary_generated = models.BooleanField(default=False)
    
    # Prakriti Analysis Results
    vata_percentage = models.FloatField(default=0.0)
    pitta_percentage = models.FloatField(default=0.0)
    kapha_percentage = models.FloatField(default=0.0)
    dominant_dosha = models.CharField(max_length=10, blank=True)
    
    # Calorie Requirements
    daily_calorie_needs = models.FloatField(default=0.0)
    breakfast_calories = models.FloatField(default=0.0)
    lunch_calories = models.FloatField(default=0.0)
    dinner_calories = models.FloatField(default=0.0)
    snack_calories = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Patient: {self.user_profile.user.get_full_name()}"
    
    @property
    def bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 2)
        return None


class DietitianProfile(models.Model):
    """Extended dietitian profile with professional information"""
    
    QUALIFICATION_CHOICES = [
        ('bsc', 'B.Sc. Nutrition'),
        ('msc', 'M.Sc. Nutrition'),
        ('phd', 'Ph.D. Nutrition'),
        ('rd', 'Registered Dietitian'),
        ('ayurvedic', 'Ayurvedic Practitioner'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='dietitian_profile')
    
    # Professional Information
    qualification = models.CharField(max_length=20, choices=QUALIFICATION_CHOICES, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    experience_years = models.IntegerField(default=0)
    bio = models.TextField(blank=True)
    
    # Practice Information
    clinic_name = models.CharField(max_length=200, blank=True)
    clinic_address = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Availability
    is_available = models.BooleanField(default=True)
    consultation_hours = models.TextField(blank=True, help_text="e.g., Mon-Fri 9AM-5PM")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dietitian: {self.user_profile.user.get_full_name()}"


class Appointment(models.Model):
    """Appointment booking system"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    TYPE_CHOICES = [
        ('in_person', 'In-Person'),
        ('virtual', 'Virtual'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='patient_appointments')
    dietitian = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='dietitian_appointments')
    
    # Appointment Details
    appointment_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='in_person')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Consultation Details
    reason_for_visit = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    
    # Virtual Meeting
    meeting_link = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    
    # Payment
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f"Appointment: {self.patient.user.get_full_name()} with {self.dietitian.user.get_full_name()}"


class PrakritiQuestion(models.Model):
    """Questions for Prakriti analysis"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_text = models.TextField()
    question_number = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['question_number']
    
    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}..."


class PrakritiOption(models.Model):
    """Answer options for Prakriti questions"""
    
    DOSHA_CHOICES = [
        ('vata', 'Vata'),
        ('pitta', 'Pitta'),
        ('kapha', 'Kapha'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(PrakritiQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.TextField()
    dosha_type = models.CharField(max_length=10, choices=DOSHA_CHOICES)
    weight = models.FloatField(default=1.0, help_text="Weight of this option for dosha calculation")
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.question.question_number} - {self.option_text[:30]}..."


class PrakritiResponse(models.Model):
    """Patient responses to Prakriti analysis"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='prakriti_responses')
    question = models.ForeignKey(PrakritiQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(PrakritiOption, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['patient', 'question']
        ordering = ['question__question_number']
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - Q{self.question.question_number}"


class DiseaseQuestion(models.Model):
    """Questions for disease analysis"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_text = models.TextField()
    question_number = models.IntegerField()
    category = models.CharField(max_length=100, blank=True, help_text="e.g., Cardiovascular, Digestive, etc.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['question_number']
    
    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}..."


class DiseaseResponse(models.Model):
    """Patient responses to disease analysis"""
    
    RESPONSE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('sometimes', 'Sometimes'),
        ('not_sure', 'Not Sure'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='disease_responses')
    question = models.ForeignKey(DiseaseQuestion, on_delete=models.CASCADE)
    response = models.CharField(max_length=20, choices=RESPONSE_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['patient', 'question']
        ordering = ['question__question_number']
    
    def __str__(self):
        return f"{self.patient.user.get_full_name()} - Q{self.question.question_number}: {self.response}"