import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
import json
import re
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Handles OCR text extraction from medical documents"""
    
    def __init__(self):
        # Configure Tesseract path for Windows
        if os.name == 'nt':  # Windows
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            else:
                # Try alternative paths
                alt_paths = [
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                    r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
                ]
                for path in alt_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        break
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            if processed_image is None:
                return ""
            
            # Configure Tesseract for medical documents
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF (requires pdf2image library)"""
        try:
            from pdf2image import convert_from_path
            
            # Convert PDF to images
            pages = convert_from_path(pdf_path, dpi=300)
            
            extracted_text = ""
            for page in pages:
                # Save page as temporary image
                temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_page.png')
                page.save(temp_path, 'PNG')
                
                # Extract text from image
                page_text = self.extract_text_from_image(temp_path)
                extracted_text += page_text + "\n"
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            return extracted_text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""


class MedicalTextAnalyzer:
    """Analyzes medical text and extracts structured information"""
    
    def __init__(self):
        self.medication_patterns = [
            r'(?i)(?:medication|drug|medicine|prescription):\s*([^\n]+)',
            r'(?i)(?:rx|prescribed):\s*([^\n]+)',
            r'(?i)(?:take|administer):\s*([^\n]+)',
        ]
        
        self.vital_signs_patterns = {
            'blood_pressure': r'(?i)(?:bp|blood pressure):\s*(\d+/\d+)',
            'heart_rate': r'(?i)(?:hr|heart rate|pulse):\s*(\d+)',
            'temperature': r'(?i)(?:temp|temperature):\s*(\d+\.?\d*)\s*°?[fFcC]',
            'weight': r'(?i)(?:weight|wt):\s*(\d+\.?\d*)\s*(?:kg|lbs?|pounds?)',
            'height': r'(?i)(?:height|ht):\s*(\d+\.?\d*)\s*(?:cm|inches?|in)',
        }
        
        self.diagnosis_patterns = [
            r'(?i)(?:diagnosis|dx|condition):\s*([^\n]+)',
            r'(?i)(?:diagnosed with):\s*([^\n]+)',
            r'(?i)(?:suffering from):\s*([^\n]+)',
        ]
    
    def extract_medications(self, text: str) -> List[Dict]:
        """Extract medication information from text"""
        medications = []
        
        for pattern in self.medication_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                medications.append({
                    'name': match.strip(),
                    'confidence': 0.8
                })
        
        return medications
    
    def extract_vital_signs(self, text: str) -> Dict:
        """Extract vital signs from text"""
        vital_signs = {}
        
        for key, pattern in self.vital_signs_patterns.items():
            match = re.search(pattern, text)
            if match:
                vital_signs[key] = {
                    'value': match.group(1),
                    'confidence': 0.9
                }
        
        return vital_signs
    
    def extract_diagnosis(self, text: str) -> List[Dict]:
        """Extract diagnosis information from text"""
        diagnoses = []
        
        for pattern in self.diagnosis_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                diagnoses.append({
                    'condition': match.strip(),
                    'confidence': 0.8
                })
        
        return diagnoses
    
    def extract_key_findings(self, text: str) -> List[str]:
        """Extract key findings from medical text"""
        # Look for common medical keywords and phrases
        key_indicators = [
            r'(?i)(?:abnormal|elevated|decreased|normal|positive|negative|significant)',
            r'(?i)(?:finding|result|observation|note)',
            r'(?i)(?:recommend|suggest|advise|indicate)',
        ]
        
        findings = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(re.search(pattern, sentence) for pattern in key_indicators):
                if len(sentence) > 10:  # Filter out very short sentences
                    findings.append(sentence)
        
        return findings[:10]  # Return top 10 findings


class AISummarizer:
    """AI-powered medical text summarization using Google Gemini"""
    
    def __init__(self):
        self.gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.model = None
        
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.genai = genai  # Store reference for later use
            except ImportError:
                logger.warning("Google Generative AI library not installed")
            except Exception as e:
                logger.error(f"Error initializing Gemini: {e}")
    
    def generate_summary(self, text: str, document_type: str) -> Dict:
        """Generate AI summary of medical document using Gemini"""
        if not self.model:
            return self._fallback_summary(text, document_type)
        
        try:
            prompt = self._create_medical_prompt(text, document_type)
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.3,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            summary = response.text.strip()
            
            return {
                'summary': summary,
                'confidence': 0.9,
                'ai_model': 'gemini-1.5-flash'
            }
            
        except Exception as e:
            logger.error(f"Error generating Gemini summary: {e}")
            return self._fallback_summary(text, document_type)
    
    def _create_medical_prompt(self, text: str, document_type: str) -> str:
        """Create prompt for medical document summarization"""
        return f"""
        Please analyze this {document_type} and provide a concise summary for a doctor. 
        Focus on:
        1. Key medical findings
        2. Medications prescribed
        3. Vital signs or lab values
        4. Diagnosis or conditions
        5. Recommendations or follow-up needed
        
        Document text:
        {text[:2000]}  # Limit text length
        
        Provide a structured summary in 3-4 sentences.
        """
    
    def _fallback_summary(self, text: str, document_type: str) -> Dict:
        """Fallback summary when AI is not available"""
        analyzer = MedicalTextAnalyzer()
        
        medications = analyzer.extract_medications(text)
        vital_signs = analyzer.extract_vital_signs(text)
        diagnosis = analyzer.extract_diagnosis(text)
        key_findings = analyzer.extract_key_findings(text)
        
        summary_parts = []
        
        if diagnosis:
            summary_parts.append(f"Diagnosis: {', '.join([d['condition'] for d in diagnosis])}")
        
        if medications:
            summary_parts.append(f"Medications: {', '.join([m['name'] for m in medications])}")
        
        if vital_signs:
            summary_parts.append(f"Vital signs recorded: {', '.join(vital_signs.keys())}")
        
        if key_findings:
            summary_parts.append(f"Key findings: {key_findings[0] if key_findings else 'None noted'}")
        
        return {
            'summary': '. '.join(summary_parts) if summary_parts else "Document processed successfully.",
            'confidence': 0.6,
            'ai_model': 'rule-based'
        }


class MedicalDocumentProcessor:
    """Main processor that coordinates OCR and AI analysis"""
    
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.text_analyzer = MedicalTextAnalyzer()
        self.ai_summarizer = AISummarizer()
    
    def process_document(self, document_path: str, document_type: str) -> Dict:
        """Process a medical document and return analysis results"""
        try:
            # Extract text using OCR
            if document_path.lower().endswith('.pdf'):
                extracted_text = self.ocr_processor.extract_text_from_pdf(document_path)
            else:
                extracted_text = self.ocr_processor.extract_text_from_image(document_path)
            
            if not extracted_text:
                return {
                    'success': False,
                    'error': 'No text could be extracted from the document'
                }
            
            # Analyze text for medical information
            medications = self.text_analyzer.extract_medications(extracted_text)
            vital_signs = self.text_analyzer.extract_vital_signs(extracted_text)
            diagnosis = self.text_analyzer.extract_diagnosis(extracted_text)
            key_findings = self.text_analyzer.extract_key_findings(extracted_text)
            
            # Generate AI summary
            ai_result = self.ai_summarizer.generate_summary(extracted_text, document_type)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                extracted_text, medications, vital_signs, diagnosis
            )
            
            return {
                'success': True,
                'extracted_text': extracted_text,
                'ai_summary': ai_result['summary'],
                'medications': medications,
                'vital_signs': vital_signs,
                'diagnosis': diagnosis,
                'key_findings': key_findings,
                'confidence_score': confidence_score,
                'ai_model_used': ai_result['ai_model']
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_confidence_score(self, text: str, medications: List, vital_signs: Dict, diagnosis: List) -> float:
        """Calculate confidence score based on extracted information"""
        score = 0.0
        
        # Base score from text length
        if len(text) > 100:
            score += 0.2
        if len(text) > 500:
            score += 0.2
        
        # Score from extracted medical information
        if medications:
            score += 0.2
        if vital_signs:
            score += 0.2
        if diagnosis:
            score += 0.2
        
        return min(score, 1.0)
