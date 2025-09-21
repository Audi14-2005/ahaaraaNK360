"""
AAHAARA Care Chatbot Services
Medical AI Assistant powered by Google Gemini
Created by: NK
"""

import google.generativeai as genai
from django.conf import settings
from django.db.models import Q
import json
import logging
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)


class NKCareAI:
    """AAHAARA Care AI Assistant for Medical Professionals"""
    
    def __init__(self):
        """Initialize AAHAARA Care AI with Gemini"""
        try:
            # Configure Gemini API
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.genai = genai
            
            # Medical context and safety guidelines
            self.medical_context = self._get_medical_context()
            self.safety_guidelines = self._get_safety_guidelines()
            
            logger.info("AAHAARA Care AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AAHAARA Care AI: {e}")
            raise
    
    def _get_medical_context(self) -> str:
        """Get medical context for the AI"""
        return """
        You are AAHAARA Care, an advanced medical AI assistant created by NK to help doctors and medical professionals.
        
        Your role:
        - Provide medical information and clarification
        - Assist with medical decision-making
        - Offer evidence-based medical insights
        - Help with differential diagnosis considerations
        - Provide medication information and interactions
        - Assist with treatment protocols and guidelines
        
        Important guidelines:
        - Always emphasize that you are an AI assistant, not a replacement for clinical judgment
        - Recommend consulting with specialists when appropriate
        - Provide evidence-based information when available
        - Be clear about limitations and uncertainties
        - Prioritize patient safety in all recommendations
        - Maintain professional medical communication standards
        """
    
    def _get_safety_guidelines(self) -> List[str]:
        """Get safety guidelines for medical AI responses"""
        return [
            "Always recommend professional medical consultation for serious conditions",
            "Never provide specific dosages without proper medical context",
            "Emphasize the importance of patient history and physical examination",
            "Suggest appropriate diagnostic tests when relevant",
            "Highlight potential drug interactions and contraindications",
            "Recommend emergency care for urgent symptoms",
            "Maintain patient confidentiality and privacy",
            "Provide evidence-based information with appropriate citations when possible"
        ]
    
    def generate_response(self, user_message: str, chat_history: List[Dict] = None, 
                         medical_context: Dict = None, patient_data: Dict = None) -> Dict:
        """Generate a medical AI response using Gemini"""
        try:
            # Build the conversation context
            conversation_context = self._build_conversation_context(
                user_message, chat_history, medical_context, patient_data
            )
            
            # Generate response with medical safety guidelines
            import time
            start_time = time.time()
            
            response = self.model.generate_content(
                conversation_context,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more consistent medical responses
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1024,
                )
            )
            
            end_time = time.time()
            logger.info(f"Gemini API call took {end_time - start_time:.2f} seconds")
            
            # Process and validate the response
            processed_response = self._process_response(response.text, user_message)
            
            return {
                'success': True,
                'response': processed_response['content'],
                'confidence_score': processed_response['confidence'],
                'medical_advice_flag': processed_response['is_medical_advice'],
                'safety_warnings': processed_response['safety_warnings'],
                'suggested_actions': processed_response['suggested_actions'],
                'ai_model': 'gemini-1.5-flash'
            }
            
        except Exception as e:
            logger.error(f"Error generating AAHAARA Care response: {e}")
            # Provide a fallback response for common medical queries
            fallback_response = self._get_fallback_response(user_message)
            return {
                'success': True,
                'response': fallback_response,
                'confidence_score': 0.5,
                'medical_advice_flag': True,
                'safety_warnings': ['AI service temporarily unavailable - please consult a medical professional'],
                'suggested_actions': ['Consult with a medical professional for accurate diagnosis'],
                'ai_model': 'fallback'
            }
    
    def _build_conversation_context(self, user_message: str, chat_history: List[Dict] = None, 
                                   medical_context: Dict = None, patient_data: Dict = None) -> str:
        """Build the full conversation context for Gemini"""
        context_parts = [self.medical_context]
        
        # Add safety guidelines
        context_parts.append("\nSafety Guidelines:")
        for guideline in self.safety_guidelines:
            context_parts.append(f"- {guideline}")
        
        # Add patient data if available
        if patient_data:
            context_parts.append(f"\nPatient Information:")
            if patient_data.get('patient_name'):
                context_parts.append(f"Patient Name: {patient_data['patient_name']}")
            if patient_data.get('patient_id'):
                context_parts.append(f"Patient ID: {patient_data['patient_id']}")
            if patient_data.get('documents'):
                context_parts.append(f"Available Documents: {len(patient_data['documents'])} documents")
                for doc in patient_data['documents'][:3]:  # Show first 3 documents
                    context_parts.append(f"- {doc.get('document_type', 'Unknown')}: {doc.get('ai_summary', 'No summary available')[:200]}...")
            if patient_data.get('summary'):
                context_parts.append(f"Patient Summary: {patient_data['summary']}")
        
        # Add medical context if provided
        if medical_context:
            context_parts.append(f"\nMedical Context: {json.dumps(medical_context)}")
        
        # Add chat history for context
        if chat_history:
            context_parts.append("\nPrevious conversation:")
            for msg in chat_history[-5:]:  # Last 5 messages for context
                role = "Doctor" if msg['message_type'] == 'user' else "AAHAARA Care"
                context_parts.append(f"{role}: {msg['content']}")
        
        # Add current user message
        context_parts.append(f"\nCurrent Doctor Question: {user_message}")
        context_parts.append("\nPlease provide a helpful, professional medical response as AAHAARA Care:")
        
        return "\n".join(context_parts)
    
    def _clean_markdown_formatting(self, text: str) -> str:
        """Clean up markdown formatting from AI responses"""
        if not text:
            return text
        
        # Remove markdown bold formatting (***text*** or **text**)
        text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'\1', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        
        # Remove markdown italic formatting (*text*)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        
        # Remove markdown headers (# ## ###)
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
        # Remove markdown list formatting (- * +)
        text = re.sub(r'^[\s]*[-*+]\s*', '• ', text, flags=re.MULTILINE)
        
        # Remove markdown code blocks (```code```)
        text = re.sub(r'```[^`]*```', '', text)
        
        # Remove markdown inline code (`code`)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove markdown links [text](url)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newlines
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single space
        text = text.strip()
        
        return text
    
    def _process_response(self, response_text: str, user_message: str) -> Dict:
        """Process and analyze the AI response for medical safety"""
        # Clean up markdown formatting from the response
        cleaned_response = self._clean_markdown_formatting(response_text)
        
        # Analyze if this contains medical advice
        medical_advice_keywords = [
            'diagnosis', 'treatment', 'medication', 'dosage', 'prescribe',
            'surgery', 'procedure', 'therapy', 'intervention', 'recommend'
        ]
        
        is_medical_advice = any(keyword in cleaned_response.lower() 
                              for keyword in medical_advice_keywords)
        
        # Extract safety warnings
        safety_warnings = self._extract_safety_warnings(cleaned_response)
        
        # Extract suggested actions
        suggested_actions = self._extract_suggested_actions(cleaned_response)
        
        # Calculate confidence score based on response quality
        confidence = self._calculate_confidence_score(cleaned_response, user_message)
        
        return {
            'content': cleaned_response,
            'confidence': confidence,
            'is_medical_advice': is_medical_advice,
            'safety_warnings': safety_warnings,
            'suggested_actions': suggested_actions
        }
    
    def _extract_safety_warnings(self, response_text: str) -> List[str]:
        """Extract safety warnings from the response"""
        warnings = []
        
        # Look for emergency indicators
        emergency_keywords = ['emergency', 'urgent', 'immediate', 'critical', 'life-threatening']
        if any(keyword in response_text.lower() for keyword in emergency_keywords):
            warnings.append("Emergency care may be required")
        
        # Look for consultation recommendations
        if 'consult' in response_text.lower() or 'specialist' in response_text.lower():
            warnings.append("Professional consultation recommended")
        
        return warnings
    
    def _extract_suggested_actions(self, response_text: str) -> List[str]:
        """Extract suggested actions from the response"""
        actions = []
        
        # Look for diagnostic suggestions
        if 'test' in response_text.lower() or 'examination' in response_text.lower():
            actions.append("Consider diagnostic testing")
        
        # Look for follow-up suggestions
        if 'follow' in response_text.lower() or 'monitor' in response_text.lower():
            actions.append("Schedule follow-up monitoring")
        
        return actions
    
    def _calculate_confidence_score(self, response_text: str, user_message: str) -> float:
        """Calculate confidence score for the response"""
        score = 0.5  # Base score
        
        # Increase score for comprehensive responses
        if len(response_text) > 100:
            score += 0.1
        
        # Increase score for evidence-based language
        evidence_keywords = ['research', 'study', 'evidence', 'guidelines', 'protocol']
        if any(keyword in response_text.lower() for keyword in evidence_keywords):
            score += 0.1
        
        # Increase score for safety disclaimers
        if 'consult' in response_text.lower() or 'professional' in response_text.lower():
            score += 0.1
        
        # Decrease score for uncertainty indicators
        uncertainty_keywords = ['uncertain', 'unclear', 'unknown', 'may be', 'could be']
        if any(keyword in response_text.lower() for keyword in uncertainty_keywords):
            score -= 0.1
        
        return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Provide a fallback response when AI service is unavailable"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['symptom', 'pain', 'ache']):
            return """I understand you're asking about symptoms. While I'm experiencing technical difficulties, here are some general guidelines:

• For chest pain, shortness of breath, or severe symptoms: Seek immediate medical attention
• For persistent symptoms: Consult with a healthcare provider
• For emergency situations: Call emergency services immediately

Please consult with a medical professional for proper evaluation and diagnosis."""
        
        elif any(word in message_lower for word in ['diagnosis', 'condition', 'disease']):
            return """I understand you're asking about diagnosis. While I'm experiencing technical difficulties, here are some general principles:

• Diagnosis requires proper medical evaluation including history, physical examination, and appropriate tests
• Self-diagnosis is not recommended
• Consult with a qualified healthcare provider for accurate diagnosis
• For urgent symptoms, seek immediate medical attention

Please consult with a medical professional for proper diagnosis and treatment."""
        
        elif any(word in message_lower for word in ['treatment', 'medicine', 'medication']):
            return """I understand you're asking about treatment. While I'm experiencing technical difficulties, here are some important points:

• Treatment should be prescribed by a qualified healthcare provider
• Do not self-medicate without professional guidance
• Follow prescribed treatment plans and dosage instructions
• Report any side effects to your healthcare provider

Please consult with a medical professional for appropriate treatment recommendations."""
        
        else:
            return """I'm AAHAARA Care, your medical AI assistant. While I'm experiencing technical difficulties, I'm here to help with medical questions and clarifications.

For your query: "{}"

Please note that:
• I'm an AI assistant and not a replacement for professional medical judgment
• Always consult with qualified healthcare providers for medical decisions
• For urgent medical concerns, seek immediate professional help
• Maintain patient confidentiality in all medical discussions

I apologize for the technical difficulty. Please try again in a moment or consult with a medical professional for immediate assistance.""".format(user_message)


class PatientDataService:
    """Service to retrieve and process patient data from medical OCR system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_patient_data(self, doctor, patient_identifier: str = None) -> Dict:
        """Retrieve patient data based on identifier"""
        try:
            from medical_ocr.models import MedicalDocument
            
            # Get all documents for the doctor
            documents = MedicalDocument.objects.filter(doctor=doctor)
            
            if patient_identifier:
                # Search by patient name or ID
                documents = documents.filter(
                    Q(patient_name__icontains=patient_identifier) |
                    Q(patient_id__icontains=patient_identifier)
                )
            
            # Get recent documents (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            documents = documents.filter(created_at__gte=thirty_days_ago)
            
            if not documents.exists():
                return {
                    'found': False,
                    'message': f"No patient data found for '{patient_identifier}'" if patient_identifier else "No recent patient data found"
                }
            
            # Group documents by patient
            patients = {}
            for doc in documents:
                patient_key = doc.patient_name or doc.patient_id or "Unknown Patient"
                if patient_key not in patients:
                    patients[patient_key] = {
                        'patient_name': doc.patient_name,
                        'patient_id': doc.patient_id,
                        'documents': [],
                        'total_documents': 0,
                        'latest_visit': None
                    }
                
                patients[patient_key]['documents'].append({
                    'id': str(doc.id),
                    'document_type': doc.document_type,
                    'ai_summary': doc.ai_summary,
                    'medications': doc.medications,
                    'vital_signs': doc.vital_signs,
                    'diagnosis': doc.diagnosis,
                    'key_findings': doc.key_findings,
                    'confidence_score': doc.confidence_score,
                    'created_at': doc.created_at.isoformat(),
                    'processing_status': doc.processing_status
                })
                
                patients[patient_key]['total_documents'] += 1
                if not patients[patient_key]['latest_visit'] or doc.created_at > patients[patient_key]['latest_visit']:
                    patients[patient_key]['latest_visit'] = doc.created_at
            
            # Generate summary for each patient
            for patient_key, patient_data in patients.items():
                patient_data['summary'] = self._generate_patient_summary(patient_data)
            
            return {
                'found': True,
                'patients': patients,
                'total_patients': len(patients)
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving patient data: {e}")
            return {
                'found': False,
                'error': str(e)
            }
    
    def _generate_patient_summary(self, patient_data: Dict) -> str:
        """Generate a comprehensive patient summary"""
        try:
            documents = patient_data['documents']
            
            # Collect key information
            all_medications = []
            all_diagnoses = []
            all_vital_signs = []
            all_findings = []
            
            for doc in documents:
                if doc.get('medications'):
                    all_medications.extend(doc['medications'].split(', ') if isinstance(doc['medications'], str) else doc['medications'])
                if doc.get('diagnosis'):
                    all_diagnoses.append(doc['diagnosis'])
                if doc.get('vital_signs'):
                    all_vital_signs.append(doc['vital_signs'])
                if doc.get('key_findings'):
                    all_findings.append(doc['key_findings'])
            
            # Create summary
            summary_parts = []
            
            if patient_data['patient_name']:
                summary_parts.append(f"Patient: {patient_data['patient_name']}")
            if patient_data['patient_id']:
                summary_parts.append(f"Patient ID: {patient_data['patient_id']}")
            
            summary_parts.append(f"Total Documents: {patient_data['total_documents']}")
            summary_parts.append(f"Latest Visit: {patient_data['latest_visit'].strftime('%Y-%m-%d') if patient_data['latest_visit'] else 'Unknown'}")
            
            if all_diagnoses:
                unique_diagnoses = list(set([d for d in all_diagnoses if d]))
                summary_parts.append(f"Diagnoses: {', '.join(unique_diagnoses[:3])}")
            
            if all_medications:
                unique_medications = list(set([m.strip() for m in all_medications if m and m.strip()]))
                summary_parts.append(f"Medications: {', '.join(unique_medications[:5])}")
            
            if all_findings:
                summary_parts.append(f"Key Findings: {all_findings[0][:200]}..." if all_findings[0] else "")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating patient summary: {e}")
            return "Summary generation failed"


class MedicalQueryAnalyzer:
    """Analyzes medical queries to provide better context"""
    
    def __init__(self):
        self.medical_categories = {
            'symptoms': ['symptom', 'pain', 'ache', 'discomfort', 'feeling'],
            'diagnosis': ['diagnosis', 'condition', 'disease', 'illness', 'disorder'],
            'treatment': ['treatment', 'therapy', 'cure', 'management', 'care'],
            'medication': ['drug', 'medicine', 'medication', 'prescription', 'dosage'],
            'procedures': ['procedure', 'surgery', 'operation', 'test', 'examination'],
            'emergency': ['emergency', 'urgent', 'critical', 'immediate', 'acute']
        }
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze a medical query to determine category and context"""
        query_lower = query.lower()
        
        # Check for patient-related queries
        patient_keywords = ['patient', 'show me patient', 'tell me about patient', 'patient data', 'patient summary', 'patient report', 'patient history']
        is_patient_query = any(keyword in query_lower for keyword in patient_keywords)
        
        # Extract patient identifier if present
        patient_identifier = None
        if is_patient_query:
            # Look for patterns like "patient John", "patient ID 123", etc.
            import re
            patterns = [
                r'patient\s+([a-zA-Z0-9\s]+)',
                r'patient\s+id\s+([a-zA-Z0-9]+)',
                r'about\s+([a-zA-Z0-9\s]+)',
                r'show\s+me\s+([a-zA-Z0-9\s]+)',
                r'tell\s+me\s+about\s+([a-zA-Z0-9\s]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    patient_identifier = match.group(1).strip()
                    break
        
        # Determine primary category
        category_scores = {}
        for category, keywords in self.medical_categories.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                category_scores[category] = score
        
        if is_patient_query:
            primary_category = 'patient_query'
        else:
            primary_category = max(category_scores, key=category_scores.get) if category_scores else 'general'
        
        # Determine urgency level
        urgency_keywords = ['emergency', 'urgent', 'critical', 'immediate', 'acute', 'severe']
        is_urgent = any(keyword in query_lower for keyword in urgency_keywords)
        
        return {
            'primary_category': primary_category,
            'category_scores': category_scores,
            'is_urgent': is_urgent,
            'is_patient_query': is_patient_query,
            'patient_identifier': patient_identifier,
            'query_length': len(query),
            'has_medical_terms': len(category_scores) > 0
        }
