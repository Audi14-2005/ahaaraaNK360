from django import forms
from .models import ChatSession, ChatMessage, MedicalKnowledgeBase, ChatFeedback


class ChatMessageForm(forms.ModelForm):
    """Form for sending chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ask AAHAARA Care anything about medical topics...',
                'id': 'message-input'
            })
        }


class ChatSessionForm(forms.ModelForm):
    """Form for creating/editing chat sessions"""
    
    class Meta:
        model = ChatSession
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter session title...'
            })
        }


class ChatFeedbackForm(forms.ModelForm):
    """Form for submitting feedback on chat messages"""
    
    class Meta:
        model = ChatFeedback
        fields = ['rating', 'feedback_text', 'is_helpful']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'feedback_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional feedback...'
            }),
            'is_helpful': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class MedicalKnowledgeBaseForm(forms.ModelForm):
    """Form for managing medical knowledge base"""
    
    class Meta:
        model = MedicalKnowledgeBase
        fields = ['category', 'title', 'content', 'keywords', 'is_active']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter medical information...'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter keywords separated by commas...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_keywords(self):
        """Convert comma-separated keywords to list"""
        keywords = self.cleaned_data.get('keywords', '')
        if keywords:
            return [keyword.strip() for keyword in keywords.split(',') if keyword.strip()]
        return []


class SearchForm(forms.Form):
    """Form for searching chat sessions and knowledge base"""
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...',
            'id': 'search-input'
        })
    )
    
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + MedicalKnowledgeBase.CATEGORIES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


