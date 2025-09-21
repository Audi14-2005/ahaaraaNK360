"""
Food Scanner AI Services
AI-powered food detection and nutritional analysis
"""
import google.generativeai as genai
from django.conf import settings
import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
import logging
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class FoodDetectionAI:
    """AI service for food detection and analysis using Gemini Vision"""
    
    def __init__(self):
        """Initialize the food detection AI"""
        try:
            # Configure Gemini API
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.genai = genai
            
            logger.info("Food Detection AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Food Detection AI: {e}")
            raise
    
    def analyze_food_image(self, image_path: str) -> Dict:
        """Analyze a food image and extract nutritional/Ayurvedic information"""
        try:
            # Load and process the image
            image = self._load_image(image_path)
            
            # Generate analysis prompt
            analysis_prompt = self._get_analysis_prompt()
            
            # Get AI analysis
            response = self.model.generate_content([
                analysis_prompt,
                image
            ])
            
            # Parse the response
            analysis_result = self._parse_analysis_response(response.text)
            
            return {
                'success': True,
                'detected_food': analysis_result.get('food_name', 'Unknown'),
                'confidence_score': analysis_result.get('confidence', 0.8),
                'nutritional_info': analysis_result.get('nutritional_info', {}),
                'ayurvedic_properties': analysis_result.get('ayurvedic_properties', {}),
                'dosha_effects': analysis_result.get('dosha_effects', {}),
                'description': analysis_result.get('description', ''),
                'recommendations': analysis_result.get('recommendations', ''),
                'warnings': analysis_result.get('warnings', ''),
            }
            
        except Exception as e:
            logger.error(f"Error analyzing food image: {e}")
            return {
                'success': False,
                'error': str(e),
                'detected_food': 'Unknown',
                'confidence_score': 0.0,
                'nutritional_info': {},
                'ayurvedic_properties': {},
                'dosha_effects': {},
                'description': '',
                'recommendations': '',
                'warnings': '',
            }
    
    def _load_image(self, image_path: str) -> Image.Image:
        """Load and preprocess the image"""
        try:
            # Load image using PIL
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (max 1024x1024)
            max_size = 1024
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            raise
    
    def _get_analysis_prompt(self) -> str:
        """Get the analysis prompt for Gemini"""
        return """
        You are an expert food analyst and Ayurvedic nutritionist. Analyze this food image and provide detailed information in the following JSON format:

        {
            "food_name": "Name of the food item",
            "confidence": 0.95,
            "nutritional_info": {
                "calories": 100.0,
                "protein": 5.0,
                "carbohydrates": 20.0,
                "fat": 2.0,
                "fiber": 3.0,
                "sugar": 8.0
            },
            "ayurvedic_properties": {
                "rasa": "sweet",
                "virya": "cooling",
                "vipaka": "sweet",
                "guna": "light, dry"
            },
            "dosha_effects": {
                "vata": "pacifies",
                "pitta": "neutral",
                "kapha": "aggravates"
            },
            "description": "Brief description of the food and its properties",
            "recommendations": "Dietary recommendations based on Ayurvedic principles",
            "warnings": "Any warnings or contraindications"
        }

        Guidelines:
        1. Identify the food item accurately
        2. Provide nutritional values per 100g
        3. Use Ayurvedic terminology for properties
        4. Determine dosha effects: pacifies, aggravates, neutral, moderate, or avoid
        5. Consider the food's heating/cooling nature
        6. Provide practical dietary advice
        7. Include any important warnings

        Respond ONLY with valid JSON format.
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the AI response and extract structured data"""
        try:
            # Clean the response text
            cleaned_text = self._clean_response_text(response_text)
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Fallback parsing if JSON extraction fails
                return self._fallback_parse(cleaned_text)
                
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return self._get_default_analysis()
    
    def _clean_response_text(self, text: str) -> str:
        """Clean the response text"""
        # Remove markdown formatting
        text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'\1', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        
        # Remove code blocks
        text = re.sub(r'```[^`]*```', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n', text)
        text = text.strip()
        
        return text
    
    def _fallback_parse(self, text: str) -> Dict:
        """Fallback parsing when JSON extraction fails"""
        # Extract basic information using regex patterns
        food_name = self._extract_pattern(text, r'food[_\s]*name["\']?\s*:\s*["\']?([^"\'}\n]+)["\']?', 'Unknown Food')
        calories = self._extract_number(text, r'calories["\']?\s*:\s*(\d+\.?\d*)', 0.0)
        protein = self._extract_number(text, r'protein["\']?\s*:\s*(\d+\.?\d*)', 0.0)
        carbohydrates = self._extract_number(text, r'carbohydrates["\']?\s*:\s*(\d+\.?\d*)', 0.0)
        fat = self._extract_number(text, r'fat["\']?\s*:\s*(\d+\.?\d*)', 0.0)
        fiber = self._extract_number(text, r'fiber["\']?\s*:\s*(\d+\.?\d*)', 0.0)
        sugar = self._extract_number(text, r'sugar["\']?\s*:\s*(\d+\.?\d*)', 0.0)
        
        rasa = self._extract_pattern(text, r'rasa["\']?\s*:\s*["\']?([^"\'}\n]+)["\']?', 'sweet')
        virya = self._extract_pattern(text, r'virya["\']?\s*:\s*["\']?([^"\'}\n]+)["\']?', 'neutral')
        vipaka = self._extract_pattern(text, r'vipaka["\']?\s*:\s*["\']?([^"\'}\n]+)["\']?', 'sweet')
        guna = self._extract_pattern(text, r'guna["\']?\s*:\s*["\']?([^"\'}\n]+)["\']?', 'light')
        
        vata_effect = self._extract_pattern(text, r'vata["\']?\s*:\s*["\']?([^"\'}\n]+)["\']?', 'neutral')
        pitta_effect = self._extract_pattern(text, r'pitta["\']?\s*:\s*["\']?([^"\'}\n]+)["\']?', 'neutral')
        kapha_effect = self._extract_pattern(text, r'kapha["\']?\s*:\s*["\']?([^"\'}\n]+)["\']?', 'neutral')
        
        return {
            'food_name': food_name,
            'confidence': 0.7,
            'nutritional_info': {
                'calories': calories,
                'protein': protein,
                'carbohydrates': carbohydrates,
                'fat': fat,
                'fiber': fiber,
                'sugar': sugar,
            },
            'ayurvedic_properties': {
                'rasa': rasa,
                'virya': virya,
                'vipaka': vipaka,
                'guna': guna,
            },
            'dosha_effects': {
                'vata': vata_effect,
                'pitta': pitta_effect,
                'kapha': kapha_effect,
            },
            'description': 'Food analysis completed',
            'recommendations': 'Consult with a nutritionist for personalized advice',
            'warnings': 'General dietary guidelines apply',
        }
    
    def _extract_pattern(self, text: str, pattern: str, default: str) -> str:
        """Extract text using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default
    
    def _extract_number(self, text: str, pattern: str, default: float) -> float:
        """Extract number using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        try:
            return float(match.group(1)) if match else default
        except (ValueError, AttributeError):
            return default
    
    def _get_default_analysis(self) -> Dict:
        """Get default analysis when parsing fails"""
        return {
            'food_name': 'Unknown Food',
            'confidence': 0.5,
            'nutritional_info': {
                'calories': 0.0,
                'protein': 0.0,
                'carbohydrates': 0.0,
                'fat': 0.0,
                'fiber': 0.0,
                'sugar': 0.0,
            },
            'ayurvedic_properties': {
                'rasa': 'sweet',
                'virya': 'neutral',
                'vipaka': 'sweet',
                'guna': 'light',
            },
            'dosha_effects': {
                'vata': 'neutral',
                'pitta': 'neutral',
                'kapha': 'neutral',
            },
            'description': 'Unable to analyze this food item',
            'recommendations': 'Please try with a clearer image or consult a nutritionist',
            'warnings': 'Analysis incomplete',
        }


class NutritionalCalculator:
    """Calculate nutritional values and serving sizes"""
    
    @staticmethod
    def calculate_per_100g(nutritional_data: Dict, serving_size: float = 100.0) -> Dict:
        """Calculate nutritional values per 100g"""
        if serving_size == 0:
            serving_size = 100.0
        
        factor = 100.0 / serving_size
        
        return {
            'calories': nutritional_data.get('calories', 0.0) * factor,
            'protein': nutritional_data.get('protein', 0.0) * factor,
            'carbohydrates': nutritional_data.get('carbohydrates', 0.0) * factor,
            'fat': nutritional_data.get('fat', 0.0) * factor,
            'fiber': nutritional_data.get('fiber', 0.0) * factor,
            'sugar': nutritional_data.get('sugar', 0.0) * factor,
        }
    
    @staticmethod
    def calculate_daily_values(nutritional_data: Dict, daily_calories: int = 2000) -> Dict:
        """Calculate daily value percentages"""
        # Standard daily values for 2000 calorie diet
        daily_values = {
            'calories': 2000,
            'protein': 50,  # grams
            'carbohydrates': 300,  # grams
            'fat': 65,  # grams
            'fiber': 25,  # grams
            'sugar': 50,  # grams
        }
        
        percentages = {}
        for nutrient, value in nutritional_data.items():
            if nutrient in daily_values:
                percentage = (value / daily_values[nutrient]) * 100
                percentages[f'{nutrient}_dv'] = min(percentage, 100)  # Cap at 100%
        
        return percentages


