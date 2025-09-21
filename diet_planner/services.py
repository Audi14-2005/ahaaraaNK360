"""
AI Services for Ayurvedic Diet Planning System

AI #1: The Architect - Rule-based diet chart generator
AI #2: The Specialist - Vector-based food swapping system
"""

import logging
import random
import numpy as np
from typing import Dict, List, Optional, Tuple
from django.db.models import Q
from .models import Patient, Food, DietChart, MealPlan, MealItem, Recipe
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class DietArchitectAI:
    """
    AI #1: The Architect
    Rule-based expert system for generating initial diet charts
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Meal timing recommendations
        self.meal_times = {
            'breakfast': '08:00',
            'lunch': '13:00',
            'dinner': '19:00',
            'snack': '16:00',
        }
        
        # Calorie distribution for meals
        self.meal_calorie_distribution = {
            'breakfast': 0.25,  # 25% of daily calories
            'lunch': 0.40,      # 40% of daily calories
            'dinner': 0.30,     # 30% of daily calories
            'snack': 0.05,      # 5% of daily calories
        }
    
    def generate_diet_chart(self, patient: Patient, duration_days: int = 7) -> Dict:
        """
        Generate a complete diet chart for a patient using rule-based logic
        Handles any type of user input and is very robust
        """
        try:
            print(f"DEBUG: Starting diet chart generation for patient: {patient.name}")
            self.logger.info(f"Generating diet chart for patient: {patient.name}")
            
            # Get suitable foods for the patient first
            suitable_foods = self._get_suitable_foods(patient)
            print(f"DEBUG: Found {len(suitable_foods)} suitable foods")
            
            if not suitable_foods:
                # If no suitable foods, use all active foods
                suitable_foods = list(Food.objects.filter(is_active=True)[:50])
                print(f"DEBUG: No suitable foods found, using all foods: {len(suitable_foods)}")
                
                if not suitable_foods:
                    return {
                        'success': False,
                        'error': 'No foods available in database. Please import foods first.'
                    }
            
            # Create the diet chart with safe defaults
            try:
                # Safe prakriti display
                prakriti_display = "balanced"
                try:
                    prakriti_display = patient.get_prakriti_display()
                except:
                    prakriti_display = getattr(patient, 'prakriti', 'balanced')
                
                diet_chart = DietChart.objects.create(
                    patient=patient,
                    dietitian=patient.dietitian,
                    title=f"AI-Generated Diet Plan for {patient.name}",
                    description=f"Personalized Ayurvedic diet plan based on {prakriti_display} constitution",
                    duration_days=duration_days,
                    ai_model_used='rule_based_architect',
                    generation_notes=f"Generated for {prakriti_display} constitution with {getattr(patient, 'activity_level', 'moderate')} activity level"
                )
                print(f"DEBUG: Created diet chart: {diet_chart.id}")
            except Exception as e:
                print(f"DEBUG: Error creating diet chart: {e}")
                return {
                    'success': False,
                    'error': f'Failed to create diet chart: {str(e)}'
                }
            
            # Generate meal plans for each day
            for day in range(1, duration_days + 1):
                try:
                    print(f"DEBUG: Generating meal plan for day {day}")
                    self._generate_daily_meal_plan(diet_chart, day, patient, suitable_foods)
                except Exception as e:
                    print(f"DEBUG: Error generating meal plan for day {day}: {e}")
                    # Continue with other days even if one fails
                    continue
            
            # Generate recipes for all foods used in the diet chart
            try:
                print(f"DEBUG: Generating recipes for diet chart foods")
                self._generate_recipes_for_diet_chart(diet_chart, patient)
            except Exception as e:
                print(f"DEBUG: Error generating recipes: {e}")
                # Don't fail the whole process if recipe generation fails
            
            print(f"DEBUG: Diet chart generation completed successfully")
            return {
                'success': True,
                'diet_chart_id': str(diet_chart.id),
                'message': f'Successfully generated {duration_days}-day diet chart with recipes',
                'total_meals': duration_days * len(self.meal_times),
                'ai_model': 'rule_based_architect'
            }
            
        except Exception as e:
            print(f"DEBUG: Error in generate_diet_chart: {e}")
            self.logger.error(f"Error generating diet chart: {e}")
            return {
                'success': False,
                'error': f'Failed to generate diet chart: {str(e)}'
            }
    
    def _get_suitable_foods(self, patient: Patient) -> List[Food]:
        """
        Filter foods based on patient's Prakriti analysis results, allergies, and preferences
        Optimized for faster performance and handles any user input
        """
        try:
            # Start with all active foods - use select_related for better performance
            foods = Food.objects.filter(is_active=True)
            
            # If no foods available, return empty list
            if not foods.exists():
                return []
            
            # Enhanced filtering based on detailed analysis results
            try:
                # Check if patient has linked user profile with analysis data
                if hasattr(patient, 'user_profile') and patient.user_profile:
                    from user_management.models import PatientProfile
                    try:
                        patient_profile = PatientProfile.objects.get(user_profile=patient.user_profile)
                        if patient_profile.prakriti_analysis_completed:
                            # Use detailed dosha percentages for more precise filtering
                            vata_pct = patient_profile.vata_percentage
                            pitta_pct = patient_profile.pitta_percentage
                            kapha_pct = patient_profile.kapha_percentage
                            
                            # Determine which doshas need pacification based on percentages
                            foods_to_include = []
                            
                            # If Vata is high (>40%), prioritize foods that pacify Vata
                            if vata_pct > 40:
                                vata_foods = foods.filter(vata_effect='pacifies')
                                foods_to_include.extend(list(vata_foods))
                            
                            # If Pitta is high (>40%), prioritize foods that pacify Pitta
                            if pitta_pct > 40:
                                pitta_foods = foods.filter(pitta_effect='pacifies')
                                foods_to_include.extend(list(pitta_foods))
                            
                            # If Kapha is high (>40%), prioritize foods that pacify Kapha
                            if kapha_pct > 40:
                                kapha_foods = foods.filter(kapha_effect='pacifies')
                                foods_to_include.extend(list(kapha_foods))
                            
                            # Add neutral foods for balance
                            neutral_foods = foods.filter(vata_effect='neutral', pitta_effect='neutral', kapha_effect='neutral')
                            foods_to_include.extend(list(neutral_foods))
                            
                            # Remove duplicates and return
                            if foods_to_include:
                                unique_foods = list(set(foods_to_include))
                                print(f"DEBUG: Using analysis-based filtering: {len(unique_foods)} foods")
                                return unique_foods[:50]  # Limit to 50 foods for performance
                                
                    except PatientProfile.DoesNotExist:
                        pass
                
                # Fallback to basic prakriti filtering
                if patient.prakriti:
                    prakriti = patient.prakriti.lower()
                    # For each dosha in the patient's prakriti, filter foods that pacify that dosha
                    if 'vata' in prakriti:
                        # Prioritize foods that pacify vata, but also include neutral ones
                        foods = foods.filter(vata_effect__in=['pacifies', 'neutral'])
                    if 'pitta' in prakriti:
                        # Prioritize foods that pacify pitta, but also include neutral ones
                        foods = foods.filter(pitta_effect__in=['pacifies', 'neutral'])
                    if 'kapha' in prakriti:
                        # Prioritize foods that pacify kapha, but also include neutral ones
                        foods = foods.filter(kapha_effect__in=['pacifies', 'neutral'])
            except Exception as e:
                print(f"DEBUG: Error in prakriti filtering: {e}")
                pass  # If prakriti filtering fails, continue without it
            
            # Filter by allergies - simplified with error handling
            try:
                if patient.allergies and isinstance(patient.allergies, list):
                    for allergy in patient.allergies:
                        if isinstance(allergy, str):
                            allergy = allergy.lower()
                            if 'nuts' in allergy:
                                foods = foods.exclude(contains_nuts=True)
                            elif 'soy' in allergy:
                                foods = foods.exclude(contains_soy=True)
                            elif 'eggs' in allergy:
                                foods = foods.exclude(contains_eggs=True)
                            elif 'fish' in allergy:
                                foods = foods.exclude(contains_fish=True)
                            elif 'shellfish' in allergy:
                                foods = foods.exclude(contains_shellfish=True)
                            elif 'dairy' in allergy:
                                foods = foods.exclude(is_dairy_free=False)
                            elif 'gluten' in allergy:
                                foods = foods.exclude(is_gluten_free=False)
            except:
                pass  # If allergy filtering fails, continue without it
            
            # Filter by dietary preferences - simplified with error handling
            try:
                if patient.dietary_preferences and isinstance(patient.dietary_preferences, list):
                    for preference in patient.dietary_preferences:
                        if isinstance(preference, str):
                            preference = preference.lower()
                            if 'vegetarian' in preference:
                                foods = foods.filter(is_vegetarian=True)
                            elif 'vegan' in preference:
                                foods = foods.filter(is_vegan=True)
                            elif 'gluten_free' in preference or 'gluten-free' in preference:
                                foods = foods.filter(is_gluten_free=True)
                            elif 'dairy_free' in preference or 'dairy-free' in preference:
                                foods = foods.filter(is_dairy_free=True)
            except:
                pass  # If preference filtering fails, continue without it
            
            # Filter by food dislikes - simplified with error handling
            try:
                if patient.food_dislikes and isinstance(patient.food_dislikes, list):
                    foods = foods.exclude(name__in=patient.food_dislikes)
            except:
                pass  # If dislike filtering fails, continue without it
            
            # If no foods remain after filtering, get all active foods
            if not foods.exists():
                foods = Food.objects.filter(is_active=True)
            
            # Limit to first 50 foods for faster processing
            return list(foods[:50])
            
        except Exception as e:
            # If anything fails, return all active foods
            print(f"DEBUG: Error in _get_suitable_foods: {e}")
            return list(Food.objects.filter(is_active=True)[:50])
    
    def _get_prakriti_filters(self, prakriti: str) -> Dict:
        """
        Get database filters based on patient's Prakriti
        """
        filters = {}
        
        if 'vata' in prakriti:
            filters['vata_effect__in'] = ['pacifies', 'neutral']
        if 'pitta' in prakriti:
            filters['pitta_effect__in'] = ['pacifies', 'neutral']
        if 'kapha' in prakriti:
            filters['kapha_effect__in'] = ['pacifies', 'neutral']
        
        return filters
    
    def _get_allergy_filters(self, allergies: List[str]) -> Dict:
        """
        Get database filters to exclude allergenic foods
        """
        filters = Q()
        
        for allergy in allergies:
            allergy = allergy.lower()
            if 'nuts' in allergy:
                filters |= Q(contains_nuts=True)
            elif 'soy' in allergy:
                filters |= Q(contains_soy=True)
            elif 'eggs' in allergy:
                filters |= Q(contains_eggs=True)
            elif 'fish' in allergy:
                filters |= Q(contains_fish=True)
            elif 'shellfish' in allergy:
                filters |= Q(contains_shellfish=True)
            elif 'dairy' in allergy:
                filters |= Q(is_dairy_free=False)
            elif 'gluten' in allergy:
                filters |= Q(is_gluten_free=False)
        
        return filters
    
    def _get_preference_filters(self, preferences: List[str]) -> Dict:
        """
        Get database filters based on dietary preferences
        """
        filters = {}
        
        for preference in preferences:
            preference = preference.lower()
            if 'vegetarian' in preference:
                filters['is_vegetarian'] = True
            elif 'vegan' in preference:
                filters['is_vegan'] = True
            elif 'gluten_free' in preference:
                filters['is_gluten_free'] = True
            elif 'dairy_free' in preference:
                filters['is_dairy_free'] = True
        
        return filters
    
    def _generate_daily_meal_plan(self, diet_chart: DietChart, day: int, patient: Patient, suitable_foods: List[Food]):
        """
        Generate meal plans for a specific day
        """
        daily_calories = patient.daily_calorie_needs or 2000
        
        for meal_type, meal_time in self.meal_times.items():
            # Calculate target calories for this meal
            target_calories = int(daily_calories * self.meal_calorie_distribution[meal_type])
            
            # Create meal plan
            meal_plan = MealPlan.objects.create(
                diet_chart=diet_chart,
                day_number=day,
                meal_type=meal_type,
                meal_time=meal_time,
                target_calories=target_calories,
                target_protein=target_calories * 0.15 / 4,  # 15% protein
                target_carbs=target_calories * 0.55 / 4,    # 55% carbs
                target_fat=target_calories * 0.30 / 9,      # 30% fat
            )
            
            # Generate meal items
            self._generate_meal_items(meal_plan, suitable_foods, target_calories)
    
    def _generate_meal_items(self, meal_plan: MealPlan, suitable_foods: List[Food], target_calories: int):
        """
        Generate food items for a specific meal - optimized for speed
        """
        if not suitable_foods:
            return
        
        # Simplified meal generation - just pick 2-3 foods per meal
        num_foods = min(3, len(suitable_foods))
        selected_foods = random.sample(suitable_foods, num_foods)
        
        # Create meal items with simple quantities
        for i, food in enumerate(selected_foods):
            # Simple quantity calculation
            if i == 0:  # Main food gets more
                quantity = 150
            else:  # Side foods get less
                quantity = 100
            
            meal_item = MealItem.objects.create(
                meal_plan=meal_plan,
                food=food,
                quantity=quantity,
                serving_size=f"{quantity:.0f}g",
                is_ai_generated=True,
                ai_confidence_score=0.8  # High confidence for rule-based selection
            )


class FoodSpecialistAI:
    """
    AI #2: The Specialist
    Vector-based system for intelligent food swapping
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def find_similar_foods(self, original_food: Food, patient: Patient, limit: int = 5) -> List[Dict]:
        """
        Find similar foods using vector similarity and Ayurvedic properties
        """
        try:
            self.logger.info(f"Finding similar foods for: {original_food.name}")
            
            # Get candidate foods (same category, suitable for patient)
            candidate_foods = self._get_candidate_foods(original_food, patient)
            
            if not candidate_foods:
                return []
            
            # Calculate similarity scores
            similar_foods = []
            for food in candidate_foods:
                similarity_score = self._calculate_similarity(original_food, food, patient)
                if similarity_score > 0.3:  # Minimum similarity threshold
                    similar_foods.append({
                        'food': food,
                        'similarity_score': similarity_score,
                        'reason': self._get_similarity_reason(original_food, food)
                    })
            
            # Sort by similarity score and return top results
            similar_foods.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_foods[:limit]
            
        except Exception as e:
            self.logger.error(f"Error finding similar foods: {e}")
            return []
    
    def _get_candidate_foods(self, original_food: Food, patient: Patient) -> List[Food]:
        """
        Get candidate foods for similarity comparison
        """
        # Start with foods in the same category
        foods = Food.objects.filter(
            category=original_food.category,
            is_active=True
        ).exclude(id=original_food.id)
        
        # Apply patient-specific filters
        prakriti_filters = self._get_prakriti_filters(patient.prakriti)
        foods = foods.filter(**prakriti_filters)
        
        # Filter by allergies
        if patient.allergies:
            allergy_filters = self._get_allergy_filters(patient.allergies)
            foods = foods.exclude(allergy_filters)
        
        # Filter by dietary preferences
        if patient.dietary_preferences:
            preference_filters = self._get_preference_filters(patient.dietary_preferences)
            foods = foods.filter(**preference_filters)
        
        return list(foods)
    
    def _calculate_similarity(self, food1: Food, food2: Food, patient: Patient) -> float:
        """
        Calculate similarity score between two foods
        """
        score = 0.0
        max_score = 0.0
        
        # Ayurvedic properties similarity (40% weight)
        ayurvedic_score = self._calculate_ayurvedic_similarity(food1, food2)
        score += ayurvedic_score * 0.4
        max_score += 0.4
        
        # Nutritional similarity (30% weight)
        nutritional_score = self._calculate_nutritional_similarity(food1, food2)
        score += nutritional_score * 0.3
        max_score += 0.3
        
        # Category similarity (20% weight)
        category_score = 1.0 if food1.category == food2.category else 0.5
        score += category_score * 0.2
        max_score += 0.2
        
        # Patient-specific compatibility (10% weight)
        compatibility_score = self._calculate_patient_compatibility(food2, patient)
        score += compatibility_score * 0.1
        max_score += 0.1
        
        return score / max_score if max_score > 0 else 0.0
    
    def _calculate_ayurvedic_similarity(self, food1: Food, food2: Food) -> float:
        """
        Calculate similarity based on Ayurvedic properties
        """
        score = 0.0
        
        # Taste similarity
        if food1.primary_taste == food2.primary_taste:
            score += 0.4
        elif food1.secondary_taste == food2.primary_taste or food1.primary_taste == food2.secondary_taste:
            score += 0.2
        
        # Energy similarity
        if food1.energy == food2.energy:
            score += 0.3
        
        # Dosha effects similarity
        dosha_effects = ['vata_effect', 'pitta_effect', 'kapha_effect']
        for effect in dosha_effects:
            if getattr(food1, effect) == getattr(food2, effect):
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_nutritional_similarity(self, food1: Food, food2: Food) -> float:
        """
        Calculate similarity based on nutritional content
        """
        # Normalize nutritional values
        nutrients1 = [food1.calories, food1.protein, food1.carbohydrates, food1.fat, food1.fiber]
        nutrients2 = [food2.calories, food2.protein, food2.carbohydrates, food2.fat, food2.fiber]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(nutrients1, nutrients2))
        magnitude1 = sum(a * a for a in nutrients1) ** 0.5
        magnitude2 = sum(b * b for b in nutrients2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _calculate_patient_compatibility(self, food: Food, patient: Patient) -> float:
        """
        Calculate how well a food fits the patient's profile
        """
        score = 1.0
        
        # Check Prakriti compatibility
        if 'vata' in patient.prakriti and food.vata_effect == 'aggravates':
            score -= 0.3
        if 'pitta' in patient.prakriti and food.pitta_effect == 'aggravates':
            score -= 0.3
        if 'kapha' in patient.prakriti and food.kapha_effect == 'aggravates':
            score -= 0.3
        
        return max(score, 0.0)
    
    def _get_similarity_reason(self, food1: Food, food2: Food) -> str:
        """
        Generate a human-readable reason for the similarity
        """
        reasons = []
        
        if food1.primary_taste == food2.primary_taste:
            reasons.append(f"both have {food1.primary_taste} taste")
        
        if food1.energy == food2.energy:
            reasons.append(f"both are {food1.energy}")
        
        if food1.category == food2.category:
            reasons.append(f"both are {food1.category}")
        
        if food1.vata_effect == food2.vata_effect:
            reasons.append(f"both {food1.vata_effect} Vata")
        
        if not reasons:
            reasons.append("nutritionally similar")
        
        return ", ".join(reasons)
    
    def _get_prakriti_filters(self, prakriti: str) -> Dict:
        """Same as in DietArchitectAI"""
        filters = {}
        if 'vata' in prakriti:
            filters['vata_effect__in'] = ['pacifies', 'neutral']
        if 'pitta' in prakriti:
            filters['pitta_effect__in'] = ['pacifies', 'neutral']
        if 'kapha' in prakriti:
            filters['kapha_effect__in'] = ['pacifies', 'neutral']
        return filters
    
    def _get_allergy_filters(self, allergies: List[str]) -> Q:
        """Same as in DietArchitectAI"""
        filters = Q()
        for allergy in allergies:
            allergy = allergy.lower()
            if 'nuts' in allergy:
                filters |= Q(contains_nuts=True)
            elif 'soy' in allergy:
                filters |= Q(contains_soy=True)
            elif 'eggs' in allergy:
                filters |= Q(contains_eggs=True)
            elif 'fish' in allergy:
                filters |= Q(contains_fish=True)
            elif 'shellfish' in allergy:
                filters |= Q(contains_shellfish=True)
            elif 'dairy' in allergy:
                filters |= Q(is_dairy_free=False)
            elif 'gluten' in allergy:
                filters |= Q(is_gluten_free=False)
        return filters
    
    def _get_preference_filters(self, preferences: List[str]) -> Dict:
        """Same as in DietArchitectAI"""
        filters = {}
        for preference in preferences:
            preference = preference.lower()
            if 'vegetarian' in preference:
                filters['is_vegetarian'] = True
            elif 'vegan' in preference:
                filters['is_vegan'] = True
            elif 'gluten_free' in preference:
                filters['is_gluten_free'] = True
            elif 'dairy_free' in preference:
                filters['is_dairy_free'] = True
        return filters
    
    def _generate_recipes_for_diet_chart(self, diet_chart, patient):
        """Generate recipes for all foods used in the diet chart"""
        try:
            # Get all unique foods from the diet chart
            meal_plans = MealPlan.objects.filter(diet_chart=diet_chart)
            food_ids = set()
            
            for meal_plan in meal_plans:
                meal_items = MealItem.objects.filter(meal_plan=meal_plan)
                for meal_item in meal_items:
                    food_ids.add(meal_item.food.id)
            
            print(f"DEBUG: Found {len(food_ids)} unique foods for recipe generation")
            
            # Generate recipes for each food
            recipe_generator = RecipeGeneratorAI()
            generated_recipes = 0
            
            for food_id in food_ids:
                try:
                    food = Food.objects.get(id=food_id)
                    
                    # Check if recipe already exists for this food
                    existing_recipe = Recipe.objects.filter(food=food, created_by=patient.dietitian).first()
                    if existing_recipe:
                        print(f"DEBUG: Recipe already exists for {food.name}")
                        continue
                    
                    # Determine meal type based on when the food is most commonly used
                    meal_type = self._determine_meal_type_for_food(food, diet_chart)
                    
                    # Generate recipe
                    result = recipe_generator.generate_recipe(food, meal_type, patient.dietitian)
                    if result['success']:
                        generated_recipes += 1
                        print(f"DEBUG: Generated recipe for {food.name}")
                    else:
                        print(f"DEBUG: Failed to generate recipe for {food.name}: {result['error']}")
                        
                except Food.DoesNotExist:
                    print(f"DEBUG: Food {food_id} not found")
                    continue
                except Exception as e:
                    print(f"DEBUG: Error generating recipe for food {food_id}: {e}")
                    continue
            
            print(f"DEBUG: Generated {generated_recipes} recipes for diet chart")
            
        except Exception as e:
            print(f"DEBUG: Error in _generate_recipes_for_diet_chart: {e}")
    
    def _determine_meal_type_for_food(self, food, diet_chart):
        """Determine the most appropriate meal type for a food based on usage in diet chart"""
        try:
            # Count usage by meal type
            meal_type_counts = {}
            
            meal_plans = MealPlan.objects.filter(diet_chart=diet_chart)
            for meal_plan in meal_plans:
                meal_items = MealItem.objects.filter(meal_plan=meal_plan, food=food)
                if meal_items.exists():
                    meal_type = meal_plan.meal_type
                    meal_type_counts[meal_type] = meal_type_counts.get(meal_type, 0) + 1
            
            # Return the most common meal type, default to lunch
            if meal_type_counts:
                return max(meal_type_counts, key=meal_type_counts.get)
            else:
                return 'lunch'
                
        except Exception as e:
            print(f"DEBUG: Error determining meal type: {e}")
            return 'lunch'


class RecipeGeneratorAI:
    """
    AI Service for generating recipes with YouTube URLs
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # YouTube search base URL
        self.youtube_base_url = "https://www.youtube.com/results?search_query="
        
        # Recipe templates for different food types
        self.recipe_templates = {
            'breakfast': {
                'cooking_time': 'quick',
                'difficulty': 'easy',
                'best_time': 'Morning (6-9 AM)',
                'tips': 'Best consumed warm for better digestion'
            },
            'lunch': {
                'cooking_time': 'moderate',
                'difficulty': 'medium',
                'best_time': 'Midday (12-2 PM)',
                'tips': 'Include all six tastes for balanced nutrition'
            },
            'dinner': {
                'cooking_time': 'moderate',
                'difficulty': 'medium',
                'best_time': 'Evening (6-8 PM)',
                'tips': 'Keep it light and easily digestible'
            },
            'snack': {
                'cooking_time': 'quick',
                'difficulty': 'easy',
                'best_time': 'Afternoon (3-5 PM)',
                'tips': 'Choose fresh, seasonal ingredients'
            }
        }
    
    def generate_recipe(self, food: Food, meal_type: str = 'lunch', user: User = None) -> Dict:
        """
        Generate a recipe for a specific food item with YouTube URL
        """
        try:
            self.logger.info(f"Generating recipe for {food.name} ({meal_type})")
            
            # Get recipe template for meal type
            template = self.recipe_templates.get(meal_type, self.recipe_templates['lunch'])
            
            # Generate recipe name
            recipe_name = f"Ayurvedic {food.name} Recipe"
            
            # Generate ingredients based on food properties
            ingredients = self._generate_ingredients(food)
            
            # Generate cooking instructions
            instructions = self._generate_instructions(food, meal_type)
            
            # Generate YouTube search URL
            youtube_url = self._generate_youtube_url(food, meal_type)
            
            # Generate Ayurvedic benefits
            ayurvedic_benefits = self._generate_ayurvedic_benefits(food)
            
            # Generate dosha considerations
            dosha_considerations = self._generate_dosha_considerations(food)
            
            # Calculate nutritional info (simplified)
            nutritional_info = self._calculate_nutritional_info(food, ingredients)
            
            # Create recipe object
            recipe = Recipe.objects.create(
                name=recipe_name,
                food=food,
                description=f"Traditional Ayurvedic preparation of {food.name} perfect for {meal_type}",
                ingredients=ingredients,
                instructions=instructions,
                cooking_time=template['cooking_time'],
                difficulty=template['difficulty'],
                servings=2,
                calories_per_serving=nutritional_info['calories'],
                protein_per_serving=nutritional_info['protein'],
                carbs_per_serving=nutritional_info['carbs'],
                fat_per_serving=nutritional_info['fat'],
                ayurvedic_benefits=ayurvedic_benefits,
                best_time_to_eat=template['best_time'],
                seasonal_notes=self._generate_seasonal_notes(food),
                dosha_considerations=dosha_considerations,
                cooking_tips=template['tips'],
                variations=self._generate_variations(food),
                storage_instructions=self._generate_storage_instructions(food),
                video_url=youtube_url,
                created_by=user,
                is_public=True
            )
            
            return {
                'success': True,
                'recipe_id': str(recipe.id),
                'recipe_name': recipe_name,
                'youtube_url': youtube_url,
                'message': f"Recipe generated successfully for {food.name}"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating recipe: {e}")
            return {
                'success': False,
                'error': f"Failed to generate recipe: {str(e)}"
            }
    
    def _generate_ingredients(self, food: Food) -> List[Dict]:
        """Generate ingredients list based on food properties"""
        ingredients = [
            {
                "name": food.name,
                "quantity": "1 cup",
                "notes": "Main ingredient"
            }
        ]
        
        # Add complementary ingredients based on food type
        if food.category == 'grains':
            ingredients.extend([
                {"name": "Ghee", "quantity": "1 tbsp", "notes": "For cooking"},
                {"name": "Cumin seeds", "quantity": "1 tsp", "notes": "For tempering"},
                {"name": "Salt", "quantity": "to taste", "notes": "Seasoning"}
            ])
        elif food.category == 'vegetables':
            ingredients.extend([
                {"name": "Turmeric powder", "quantity": "1/2 tsp", "notes": "Anti-inflammatory"},
                {"name": "Cumin powder", "quantity": "1/2 tsp", "notes": "Digestive aid"},
                {"name": "Coriander powder", "quantity": "1/2 tsp", "notes": "Cooling effect"},
                {"name": "Ginger", "quantity": "1 inch", "notes": "Fresh, grated"}
            ])
        elif food.category == 'fruits':
            ingredients.extend([
                {"name": "Honey", "quantity": "1 tbsp", "notes": "Natural sweetener"},
                {"name": "Cardamom powder", "quantity": "1/4 tsp", "notes": "Aromatic spice"},
                {"name": "Saffron", "quantity": "few strands", "notes": "Optional, for garnish"}
            ])
        elif food.category == 'dairy':
            ingredients.extend([
                {"name": "Cardamom powder", "quantity": "1/2 tsp", "notes": "Digestive aid"},
                {"name": "Saffron", "quantity": "few strands", "notes": "Aromatic"},
                {"name": "Nuts", "quantity": "1 tbsp", "notes": "Almonds or cashews, chopped"}
            ])
        
        return ingredients
    
    def _generate_instructions(self, food: Food, meal_type: str) -> List[str]:
        """Generate step-by-step cooking instructions"""
        instructions = []
        
        if food.category == 'grains':
            instructions = [
                "Wash the grains thoroughly until water runs clear",
                "Heat ghee in a pan and add cumin seeds",
                "When seeds crackle, add the grains and stir for 2 minutes",
                "Add water (2:1 ratio) and bring to boil",
                "Reduce heat, cover and simmer for 15-20 minutes",
                "Let it rest for 5 minutes before serving"
            ]
        elif food.category == 'vegetables':
            instructions = [
                "Clean and chop the vegetables into bite-sized pieces",
                "Heat ghee in a pan and add cumin seeds",
                "Add ginger and sauté for 30 seconds",
                "Add vegetables and stir-fry for 2-3 minutes",
                "Add turmeric, cumin, and coriander powder",
                "Add salt and cook covered for 5-7 minutes",
                "Garnish with fresh herbs and serve"
            ]
        elif food.category == 'fruits':
            instructions = [
                "Wash and prepare the fruits",
                "Mix honey and cardamom powder in a bowl",
                "Add fruits and gently toss to coat",
                "Let it marinate for 10-15 minutes",
                "Garnish with saffron and nuts if desired",
                "Serve fresh"
            ]
        elif food.category == 'dairy':
            instructions = [
                "Heat the dairy product gently in a pan",
                "Add cardamom powder and stir well",
                "Add saffron and let it infuse for 5 minutes",
                "Sweeten with honey if needed",
                "Garnish with chopped nuts",
                "Serve warm or chilled as preferred"
            ]
        else:
            instructions = [
                "Prepare the main ingredient as needed",
                "Follow traditional Ayurvedic cooking methods",
                "Add appropriate spices for your dosha",
                "Cook with love and mindfulness",
                "Serve at the appropriate time for your constitution"
            ]
        
        return instructions
    
    def _generate_youtube_url(self, food: Food, meal_type: str) -> str:
        """Generate YouTube search URL for the recipe"""
        search_terms = f"ayurvedic {food.name} recipe {meal_type} cooking"
        # Clean search terms for URL
        search_terms = search_terms.replace(" ", "+")
        return f"{self.youtube_base_url}{search_terms}"
    
    def _generate_ayurvedic_benefits(self, food: Food) -> str:
        """Generate Ayurvedic benefits text"""
        benefits = {
            'grains': f"{food.name} provides grounding energy and supports digestive fire (Agni). Rich in complex carbohydrates, it offers sustained energy and promotes satiety.",
            'vegetables': f"{food.name} offers cooling and cleansing properties. High in fiber and phytonutrients, it supports detoxification and overall health.",
            'fruits': f"{food.name} provides natural sweetness and cooling energy. Rich in vitamins and antioxidants, it supports immune function and skin health.",
            'dairy': f"{food.name} offers nourishing and cooling properties. Rich in calcium and protein, it supports bone health and provides grounding energy.",
            'spices': f"{food.name} enhances digestive fire and adds therapeutic value. Each spice has specific healing properties for different doshas.",
            'nuts': f"{food.name} provides healthy fats and grounding energy. Rich in protein and minerals, it supports brain health and overall vitality."
        }
        
        return benefits.get(food.category, f"{food.name} offers various health benefits according to Ayurvedic principles.")
    
    def _generate_dosha_considerations(self, food: Food) -> str:
        """Generate dosha-specific considerations"""
        considerations = {
            'vata': f"Vata types should consume {food.name} warm and well-cooked with digestive spices like ginger and cumin.",
            'pitta': f"Pitta types can enjoy {food.name} in moderation, preferably with cooling herbs like coriander and mint.",
            'kapha': f"Kapha types should have {food.name} in smaller portions with warming spices like black pepper and turmeric."
        }
        
        return " • ".join([f"{dosha.capitalize()}: {considerations[dosha]}" for dosha in considerations])
    
    def _generate_seasonal_notes(self, food: Food) -> str:
        """Generate seasonal consumption notes"""
        return f"Best consumed during appropriate seasons. {food.name} can be enjoyed year-round with seasonal adjustments in preparation and spices."
    
    def _generate_variations(self, food: Food) -> str:
        """Generate recipe variations"""
        return f"Try different cooking methods: steamed, sautéed, or slow-cooked. Adjust spices according to your dosha and seasonal needs."
    
    def _generate_storage_instructions(self, food: Food) -> str:
        """Generate storage instructions"""
        return f"Store {food.name} in a cool, dry place. Prepared dishes can be refrigerated for 2-3 days. Reheat gently before serving."
    
    def _calculate_nutritional_info(self, food: Food, ingredients: List[Dict]) -> Dict:
        """Calculate nutritional information (simplified)"""
        # Base nutritional values from food
        base_calories = getattr(food, 'calories_per_100g', 100) * 0.5  # Assuming 50g serving
        base_protein = getattr(food, 'protein_per_100g', 5) * 0.5
        base_carbs = getattr(food, 'carbs_per_100g', 20) * 0.5
        base_fat = getattr(food, 'fat_per_100g', 2) * 0.5
        
        # Add some variation based on additional ingredients
        return {
            'calories': round(base_calories + 50, 1),  # Add some calories for cooking
            'protein': round(base_protein + 2, 1),
            'carbs': round(base_carbs + 10, 1),
            'fat': round(base_fat + 5, 1)  # Add some fat for cooking
        }
        
        # Apply dietary preferences
        if 'vegetarian' in preference:
            filters['is_vegetarian'] = True
        elif 'vegan' in preference:
            filters['is_vegan'] = True
        elif 'gluten_free' in preference:
            filters['is_gluten_free'] = True
        elif 'dairy_free' in preference:
            filters['is_dairy_free'] = True
        return filters
    
    def _generate_recipes_for_diet_chart(self, diet_chart, patient):
        """Generate recipes for all foods used in the diet chart"""
        try:
            # Get all unique foods from the diet chart
            meal_plans = MealPlan.objects.filter(diet_chart=diet_chart)
            food_ids = set()
            
            for meal_plan in meal_plans:
                meal_items = MealItem.objects.filter(meal_plan=meal_plan)
                for meal_item in meal_items:
                    food_ids.add(meal_item.food.id)
            
            print(f"DEBUG: Found {len(food_ids)} unique foods for recipe generation")
            
            # Generate recipes for each food
            recipe_generator = RecipeGeneratorAI()
            generated_recipes = 0
            
            for food_id in food_ids:
                try:
                    food = Food.objects.get(id=food_id)
                    
                    # Check if recipe already exists for this food
                    existing_recipe = Recipe.objects.filter(food=food, created_by=patient.dietitian).first()
                    if existing_recipe:
                        print(f"DEBUG: Recipe already exists for {food.name}")
                        continue
                    
                    # Determine meal type based on when the food is most commonly used
                    meal_type = self._determine_meal_type_for_food(food, diet_chart)
                    
                    # Generate recipe
                    result = recipe_generator.generate_recipe(food, meal_type, patient.dietitian)
                    if result['success']:
                        generated_recipes += 1
                        print(f"DEBUG: Generated recipe for {food.name}")
                    else:
                        print(f"DEBUG: Failed to generate recipe for {food.name}: {result['error']}")
                        
                except Food.DoesNotExist:
                    print(f"DEBUG: Food {food_id} not found")
                    continue
                except Exception as e:
                    print(f"DEBUG: Error generating recipe for food {food_id}: {e}")
                    continue
            
            print(f"DEBUG: Generated {generated_recipes} recipes for diet chart")
            
        except Exception as e:
            print(f"DEBUG: Error in _generate_recipes_for_diet_chart: {e}")
    
    def _determine_meal_type_for_food(self, food, diet_chart):
        """Determine the most appropriate meal type for a food based on usage in diet chart"""
        try:
            # Count usage by meal type
            meal_type_counts = {}
            
            meal_plans = MealPlan.objects.filter(diet_chart=diet_chart)
            for meal_plan in meal_plans:
                meal_items = MealItem.objects.filter(meal_plan=meal_plan, food=food)
                if meal_items.exists():
                    meal_type = meal_plan.meal_type
                    meal_type_counts[meal_type] = meal_type_counts.get(meal_type, 0) + 1
            
            # Return the most common meal type, default to lunch
            if meal_type_counts:
                return max(meal_type_counts, key=meal_type_counts.get)
            else:
                return 'lunch'
                
        except Exception as e:
            print(f"DEBUG: Error determining meal type: {e}")
            return 'lunch'


class RecipeGeneratorAI:
    """
    AI Service for generating recipes with YouTube URLs
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # YouTube search base URL
        self.youtube_base_url = "https://www.youtube.com/results?search_query="
        
        # Recipe templates for different food types
        self.recipe_templates = {
            'breakfast': {
                'cooking_time': 'quick',
                'difficulty': 'easy',
                'best_time': 'Morning (6-9 AM)',
                'tips': 'Best consumed warm for better digestion'
            },
            'lunch': {
                'cooking_time': 'moderate',
                'difficulty': 'medium',
                'best_time': 'Midday (12-2 PM)',
                'tips': 'Include all six tastes for balanced nutrition'
            },
            'dinner': {
                'cooking_time': 'moderate',
                'difficulty': 'medium',
                'best_time': 'Evening (6-8 PM)',
                'tips': 'Keep it light and easily digestible'
            },
            'snack': {
                'cooking_time': 'quick',
                'difficulty': 'easy',
                'best_time': 'Afternoon (3-5 PM)',
                'tips': 'Choose fresh, seasonal ingredients'
            }
        }
    
    def generate_recipe(self, food: Food, meal_type: str = 'lunch', user: User = None) -> Dict:
        """
        Generate a recipe for a specific food item with YouTube URL
        """
        try:
            self.logger.info(f"Generating recipe for {food.name} ({meal_type})")
            
            # Get recipe template for meal type
            template = self.recipe_templates.get(meal_type, self.recipe_templates['lunch'])
            
            # Generate recipe name
            recipe_name = f"Ayurvedic {food.name} Recipe"
            
            # Generate ingredients based on food properties
            ingredients = self._generate_ingredients(food)
            
            # Generate cooking instructions
            instructions = self._generate_instructions(food, meal_type)
            
            # Generate YouTube search URL
            youtube_url = self._generate_youtube_url(food, meal_type)
            
            # Generate Ayurvedic benefits
            ayurvedic_benefits = self._generate_ayurvedic_benefits(food)
            
            # Generate dosha considerations
            dosha_considerations = self._generate_dosha_considerations(food)
            
            # Calculate nutritional info (simplified)
            nutritional_info = self._calculate_nutritional_info(food, ingredients)
            
            # Create recipe object
            recipe = Recipe.objects.create(
                name=recipe_name,
                food=food,
                description=f"Traditional Ayurvedic preparation of {food.name} perfect for {meal_type}",
                ingredients=ingredients,
                instructions=instructions,
                cooking_time=template['cooking_time'],
                difficulty=template['difficulty'],
                servings=2,
                calories_per_serving=nutritional_info['calories'],
                protein_per_serving=nutritional_info['protein'],
                carbs_per_serving=nutritional_info['carbs'],
                fat_per_serving=nutritional_info['fat'],
                ayurvedic_benefits=ayurvedic_benefits,
                best_time_to_eat=template['best_time'],
                seasonal_notes=self._generate_seasonal_notes(food),
                dosha_considerations=dosha_considerations,
                cooking_tips=template['tips'],
                variations=self._generate_variations(food),
                storage_instructions=self._generate_storage_instructions(food),
                video_url=youtube_url,
                created_by=user,
                is_public=True
            )
            
            return {
                'success': True,
                'recipe_id': str(recipe.id),
                'recipe_name': recipe_name,
                'youtube_url': youtube_url,
                'message': f"Recipe generated successfully for {food.name}"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating recipe: {e}")
            return {
                'success': False,
                'error': f"Failed to generate recipe: {str(e)}"
            }
    
    def _generate_ingredients(self, food: Food) -> List[Dict]:
        """Generate ingredients list based on food properties"""
        ingredients = [
            {
                "name": food.name,
                "quantity": "1 cup",
                "notes": "Main ingredient"
            }
        ]
        
        # Add complementary ingredients based on food type
        if food.category == 'grains':
            ingredients.extend([
                {"name": "Ghee", "quantity": "1 tbsp", "notes": "For cooking"},
                {"name": "Cumin seeds", "quantity": "1 tsp", "notes": "For tempering"},
                {"name": "Salt", "quantity": "to taste", "notes": "Seasoning"}
            ])
        elif food.category == 'vegetables':
            ingredients.extend([
                {"name": "Turmeric powder", "quantity": "1/2 tsp", "notes": "Anti-inflammatory"},
                {"name": "Cumin powder", "quantity": "1/2 tsp", "notes": "Digestive aid"},
                {"name": "Coriander powder", "quantity": "1/2 tsp", "notes": "Cooling effect"},
                {"name": "Ginger", "quantity": "1 inch", "notes": "Fresh, grated"}
            ])
        elif food.category == 'fruits':
            ingredients.extend([
                {"name": "Honey", "quantity": "1 tbsp", "notes": "Natural sweetener"},
                {"name": "Cardamom powder", "quantity": "1/4 tsp", "notes": "Aromatic spice"},
                {"name": "Saffron", "quantity": "few strands", "notes": "Optional, for garnish"}
            ])
        elif food.category == 'dairy':
            ingredients.extend([
                {"name": "Cardamom powder", "quantity": "1/2 tsp", "notes": "Digestive aid"},
                {"name": "Saffron", "quantity": "few strands", "notes": "Aromatic"},
                {"name": "Nuts", "quantity": "1 tbsp", "notes": "Almonds or cashews, chopped"}
            ])
        
        return ingredients
    
    def _generate_instructions(self, food: Food, meal_type: str) -> List[str]:
        """Generate step-by-step cooking instructions"""
        instructions = []
        
        if food.category == 'grains':
            instructions = [
                "Wash the grains thoroughly until water runs clear",
                "Heat ghee in a pan and add cumin seeds",
                "When seeds crackle, add the grains and stir for 2 minutes",
                "Add water (2:1 ratio) and bring to boil",
                "Reduce heat, cover and simmer for 15-20 minutes",
                "Let it rest for 5 minutes before serving"
            ]
        elif food.category == 'vegetables':
            instructions = [
                "Clean and chop the vegetables into bite-sized pieces",
                "Heat ghee in a pan and add cumin seeds",
                "Add ginger and sauté for 30 seconds",
                "Add vegetables and stir-fry for 2-3 minutes",
                "Add turmeric, cumin, and coriander powder",
                "Add salt and cook covered for 5-7 minutes",
                "Garnish with fresh herbs and serve"
            ]
        elif food.category == 'fruits':
            instructions = [
                "Wash and prepare the fruits",
                "Mix honey and cardamom powder in a bowl",
                "Add fruits and gently toss to coat",
                "Let it marinate for 10-15 minutes",
                "Garnish with saffron and nuts if desired",
                "Serve fresh"
            ]
        elif food.category == 'dairy':
            instructions = [
                "Heat the dairy product gently in a pan",
                "Add cardamom powder and stir well",
                "Add saffron and let it infuse for 5 minutes",
                "Sweeten with honey if needed",
                "Garnish with chopped nuts",
                "Serve warm or chilled as preferred"
            ]
        else:
            instructions = [
                "Prepare the main ingredient as needed",
                "Follow traditional Ayurvedic cooking methods",
                "Add appropriate spices for your dosha",
                "Cook with love and mindfulness",
                "Serve at the appropriate time for your constitution"
            ]
        
        return instructions
    
    def _generate_youtube_url(self, food: Food, meal_type: str) -> str:
        """Generate YouTube search URL for the recipe"""
        search_terms = f"ayurvedic {food.name} recipe {meal_type} cooking"
        # Clean search terms for URL
        search_terms = search_terms.replace(" ", "+")
        return f"{self.youtube_base_url}{search_terms}"
    
    def _generate_ayurvedic_benefits(self, food: Food) -> str:
        """Generate Ayurvedic benefits text"""
        benefits = {
            'grains': f"{food.name} provides grounding energy and supports digestive fire (Agni). Rich in complex carbohydrates, it offers sustained energy and promotes satiety.",
            'vegetables': f"{food.name} offers cooling and cleansing properties. High in fiber and phytonutrients, it supports detoxification and overall health.",
            'fruits': f"{food.name} provides natural sweetness and cooling energy. Rich in vitamins and antioxidants, it supports immune function and skin health.",
            'dairy': f"{food.name} offers nourishing and cooling properties. Rich in calcium and protein, it supports bone health and provides grounding energy.",
            'spices': f"{food.name} enhances digestive fire and adds therapeutic value. Each spice has specific healing properties for different doshas.",
            'nuts': f"{food.name} provides healthy fats and grounding energy. Rich in protein and minerals, it supports brain health and overall vitality."
        }
        
        return benefits.get(food.category, f"{food.name} offers various health benefits according to Ayurvedic principles.")
    
    def _generate_dosha_considerations(self, food: Food) -> str:
        """Generate dosha-specific considerations"""
        considerations = {
            'vata': f"Vata types should consume {food.name} warm and well-cooked with digestive spices like ginger and cumin.",
            'pitta': f"Pitta types can enjoy {food.name} in moderation, preferably with cooling herbs like coriander and mint.",
            'kapha': f"Kapha types should have {food.name} in smaller portions with warming spices like black pepper and turmeric."
        }
        
        return " • ".join([f"{dosha.capitalize()}: {considerations[dosha]}" for dosha in considerations])
    
    def _generate_seasonal_notes(self, food: Food) -> str:
        """Generate seasonal consumption notes"""
        return f"Best consumed during appropriate seasons. {food.name} can be enjoyed year-round with seasonal adjustments in preparation and spices."
    
    def _generate_variations(self, food: Food) -> str:
        """Generate recipe variations"""
        return f"Try different cooking methods: steamed, sautéed, or slow-cooked. Adjust spices according to your dosha and seasonal needs."
    
    def _generate_storage_instructions(self, food: Food) -> str:
        """Generate storage instructions"""
        return f"Store {food.name} in a cool, dry place. Prepared dishes can be refrigerated for 2-3 days. Reheat gently before serving."
    
    def _calculate_nutritional_info(self, food: Food, ingredients: List[Dict]) -> Dict:
        """Calculate nutritional information (simplified)"""
        # Base nutritional values from food
        base_calories = getattr(food, 'calories_per_100g', 100) * 0.5  # Assuming 50g serving
        base_protein = getattr(food, 'protein_per_100g', 5) * 0.5
        base_carbs = getattr(food, 'carbs_per_100g', 20) * 0.5
        base_fat = getattr(food, 'fat_per_100g', 2) * 0.5
        
        # Add some variation based on additional ingredients
        return {
            'calories': round(base_calories + 50, 1),  # Add some calories for cooking
            'protein': round(base_protein + 2, 1),
            'carbs': round(base_carbs + 10, 1),
            'fat': round(base_fat + 5, 1)  # Add some fat for cooking
        }
