"""
Recipe Generation Service
Simple AI service for generating cooking recipes without medical restrictions
"""

import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class RecipeGeneratorAI:
    """Simple AI service for generating cooking recipes"""
    
    def __init__(self):
        """Initialize Recipe Generator AI with Gemini"""
        try:
            # Configure Gemini API
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.genai = genai
            
            logger.info("Recipe Generator AI initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Recipe Generator AI: {e}")
            raise
    
    def generate_recipe(self, food_name: str, food_details: dict, user_request: str = "") -> dict:
        """Generate a cooking recipe for a specific food"""
        try:
            # Create recipe-focused prompt
            recipe_prompt = f"""
            You are a professional chef and Ayurvedic cooking expert. Create a detailed cooking recipe for {food_name}.
            
            Food Information:
            - Name: {food_name}
            - Category: {food_details.get('category', 'Unknown')}
            - Calories per 100g: {food_details.get('calories', 'Unknown')}
            - Protein: {food_details.get('protein', 'Unknown')}g
            - Carbohydrates: {food_details.get('carbohydrates', 'Unknown')}g
            - Fat: {food_details.get('fat', 'Unknown')}g
            - Primary Taste: {food_details.get('primary_taste', 'Unknown')}
            - Energy: {food_details.get('energy', 'Unknown')}
            - Vata Effect: {food_details.get('vata_effect', 'Unknown')}
            - Pitta Effect: {food_details.get('pitta_effect', 'Unknown')}
            - Kapha Effect: {food_details.get('kapha_effect', 'Unknown')}
            
            User Request: {user_request or 'Create a healthy and delicious recipe'}
            
            Please provide a complete cooking recipe with the following structure:
            
            **Recipe Name:** [Creative name for the dish]
            
            **Description:** [Brief description of the dish]
            
            **Food Image:** [Suggest a descriptive image for this dish, e.g., "Golden flaxseed porridge in a white bowl with fresh berries"]
            
            **YouTube Video:** [Suggest a relevant YouTube video title and provide a search query for finding cooking videos, e.g., "Search: 'flaxseed porridge recipe cooking tutorial'"]
            
            **Ingredients:**
            - [List all ingredients with exact quantities]
            
            **Instructions:**
            1. [Step-by-step cooking instructions]
            
            **Cooking Time:** [Total time needed]
            **Difficulty:** [Easy/Medium/Hard]
            **Servings:** [Number of servings]
            
            **Nutritional Information (per serving):**
            - Calories: [estimated]
            - Protein: [estimated]
            - Carbs: [estimated]
            - Fat: [estimated]
            
            **Ayurvedic Benefits:**
            [Explain the Ayurvedic benefits and dosha considerations]
            
            **Best Time to Consume:**
            [When this dish is best consumed]
            
            **Cooking Tips:**
            [Helpful cooking tips and variations]
            
            **Storage Instructions:**
            [How to store leftovers]
            
            **Visual Guide:**
            [Suggest what the final dish should look like and any presentation tips]
            
            Make the recipe practical, delicious, and easy to follow. Focus on traditional cooking methods and Ayurvedic principles. Include visual and video suggestions to help users learn better.
            """
            
            # Generate response
            response = self.model.generate_content(
                recipe_prompt,
                generation_config=self.genai.types.GenerationConfig(
                    temperature=0.7,  # Slightly higher for creativity
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            # Extract YouTube search query from response
            youtube_search = self._extract_youtube_search(response.text, food_name)
            
            return {
                'success': True,
                'content': response.text,
                'confidence': 0.9,
                'ai_model': 'gemini-1.5-flash',
                'youtube_search': youtube_search,
                'youtube_url': f"https://www.youtube.com/results?search_query={youtube_search.replace(' ', '+')}"
            }
            
        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': f"Sorry, I couldn't generate a recipe for {food_name} at the moment. Please try again later.",
                'confidence': 0.0
            }
    
    def _extract_youtube_search(self, recipe_text: str, food_name: str) -> str:
        """Extract YouTube search query from recipe text"""
        import re
        
        # Look for YouTube search suggestions in the text
        youtube_pattern = r'YouTube Video[:\s]*.*?Search[:\s]*["\']([^"\']+)["\']'
        match = re.search(youtube_pattern, recipe_text, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        # Fallback: create a generic search query
        return f"{food_name} recipe cooking tutorial"
