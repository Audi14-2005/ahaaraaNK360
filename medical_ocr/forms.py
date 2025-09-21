from django import forms
from .models import MedicalDocument, DoctorProfile


class MedicalDocumentForm(forms.ModelForm):
    class Meta:
        model = MedicalDocument
        fields = ['patient_name', 'patient_id', 'document_type', 'original_file']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter patient name'
            }),
            'patient_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Patient ID (optional)'
            }),
            'document_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'original_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.png,.jpg,.jpeg,.tiff'
            })
        }
        labels = {
            'patient_name': 'Patient Name',
            'patient_id': 'Patient ID',
            'document_type': 'Document Type',
            'original_file': 'Upload Document'
        }


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['medical_license', 'specialization', 'hospital_affiliation', 'phone_number']
        widgets = {
            'medical_license': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medical License Number'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Cardiology, Neurology, etc.'
            }),
            'hospital_affiliation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hospital or Clinic Name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            })
        }


class DocumentSearchForm(forms.Form):
    patient_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by patient name'
        })
    )
    document_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + MedicalDocument.DOCUMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


