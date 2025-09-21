from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from diet_planner.models import Food, Recipe
import json


class Command(BaseCommand):
    help = 'Populate sample recipes for foods'

    def handle(self, *args, **options):
        # Get or create a user for recipes
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        
        # Sample recipes data
        sample_recipes = [
            {
                'food_name': 'Basmati Rice',
                'recipe_name': 'Perfect Basmati Rice',
                'description': 'Fluffy and aromatic basmati rice cooked to perfection',
                'ingredients': [
                    {'name': 'Basmati Rice', 'quantity': '1 cup'},
                    {'name': 'Water', 'quantity': '2 cups'},
                    {'name': 'Salt', 'quantity': '1/2 tsp'},
                    {'name': 'Ghee', 'quantity': '1 tbsp'},
                ],
                'instructions': [
                    'Rinse the basmati rice until water runs clear',
                    'Soak rice for 30 minutes, then drain',
                    'Heat ghee in a pot and add rice',
                    'Add water and salt, bring to boil',
                    'Cover and simmer on low heat for 15 minutes',
                    'Let it rest for 5 minutes before fluffing with fork'
                ],
                'cooking_time': 'moderate',
                'difficulty': 'easy',
                'servings': 4,
                'calories_per_serving': 200,
                'protein_per_serving': 4.0,
                'carbs_per_serving': 45.0,
                'fat_per_serving': 0.5,
                'ayurvedic_benefits': 'Easily digestible, cooling for Pitta, grounding for Vata',
                'best_time_to_eat': 'Lunch or Dinner',
                'seasonal_notes': 'Good for all seasons, especially cooling in summer',
                'dosha_considerations': 'Pacifies Pitta and Vata, neutral for Kapha',
                'cooking_tips': 'Soaking rice improves texture and reduces cooking time',
                'variations': 'Add cumin seeds or bay leaves for extra flavor',
                'storage_instructions': 'Store in refrigerator for up to 3 days'
            },
            {
                'food_name': 'Apple',
                'recipe_name': 'Ayurvedic Apple Compote',
                'description': 'Warm, spiced apple compote perfect for balancing Vata',
                'ingredients': [
                    {'name': 'Apples', 'quantity': '4 medium'},
                    {'name': 'Water', 'quantity': '1/2 cup'},
                    {'name': 'Cinnamon', 'quantity': '1 tsp'},
                    {'name': 'Cardamom', 'quantity': '1/2 tsp'},
                    {'name': 'Ghee', 'quantity': '1 tbsp'},
                    {'name': 'Honey', 'quantity': '2 tbsp'},
                ],
                'instructions': [
                    'Peel and core apples, cut into chunks',
                    'Heat ghee in a pan and add apple chunks',
                    'Add water and spices, cover and cook on medium heat',
                    'Stir occasionally until apples are soft (10-15 minutes)',
                    'Add honey and mix well',
                    'Serve warm'
                ],
                'cooking_time': 'quick',
                'difficulty': 'easy',
                'servings': 4,
                'calories_per_serving': 120,
                'protein_per_serving': 0.5,
                'carbs_per_serving': 30.0,
                'fat_per_serving': 3.0,
                'ayurvedic_benefits': 'Warming, digestive, good for Vata constitution',
                'best_time_to_eat': 'Morning or as dessert',
                'seasonal_notes': 'Excellent in winter and fall, warming for cold seasons',
                'dosha_considerations': 'Pacifies Vata, moderate for Pitta, avoid excess for Kapha',
                'cooking_tips': 'Don\'t overcook to maintain some texture',
                'variations': 'Add raisins or nuts for extra nutrition',
                'storage_instructions': 'Refrigerate for up to 5 days, reheat before serving'
            },
            {
                'food_name': 'Ginger',
                'recipe_name': 'Ayurvedic Ginger Tea',
                'description': 'Warming ginger tea for digestion and immunity',
                'ingredients': [
                    {'name': 'Fresh Ginger', 'quantity': '1 inch piece'},
                    {'name': 'Water', 'quantity': '2 cups'},
                    {'name': 'Honey', 'quantity': '1 tbsp'},
                    {'name': 'Lemon', 'quantity': '1/2 piece'},
                    {'name': 'Black Pepper', 'quantity': '1/4 tsp'},
                ],
                'instructions': [
                    'Wash and slice ginger thinly',
                    'Boil water in a pot',
                    'Add ginger slices and black pepper',
                    'Simmer for 10-15 minutes',
                    'Strain the tea',
                    'Add honey and lemon juice',
                    'Serve hot'
                ],
                'cooking_time': 'quick',
                'difficulty': 'easy',
                'servings': 2,
                'calories_per_serving': 25,
                'protein_per_serving': 0.2,
                'carbs_per_serving': 6.0,
                'fat_per_serving': 0.1,
                'ayurvedic_benefits': 'Digestive, warming, immune boosting, anti-inflammatory',
                'best_time_to_eat': 'Morning or after meals',
                'seasonal_notes': 'Excellent in winter and monsoon, warming for cold weather',
                'dosha_considerations': 'Pacifies Kapha and Vata, use moderately for Pitta',
                'cooking_tips': 'Don\'t boil too long to avoid bitterness',
                'variations': 'Add mint leaves or tulsi for extra benefits',
                'storage_instructions': 'Best consumed fresh, can be stored in refrigerator for 1 day'
            },
            {
                'food_name': 'Almond Milk',
                'recipe_name': 'Homemade Almond Milk',
                'description': 'Creamy, nutritious almond milk made from scratch',
                'ingredients': [
                    {'name': 'Raw Almonds', 'quantity': '1 cup'},
                    {'name': 'Water', 'quantity': '4 cups'},
                    {'name': 'Honey', 'quantity': '2 tbsp'},
                    {'name': 'Vanilla Extract', 'quantity': '1 tsp'},
                    {'name': 'Salt', 'quantity': '1 pinch'},
                ],
                'instructions': [
                    'Soak almonds in water overnight or for 8 hours',
                    'Drain and rinse almonds',
                    'Blend almonds with fresh water until smooth',
                    'Strain through cheesecloth or nut milk bag',
                    'Add honey, vanilla, and salt',
                    'Store in refrigerator for up to 5 days'
                ],
                'cooking_time': 'quick',
                'difficulty': 'easy',
                'servings': 4,
                'calories_per_serving': 80,
                'protein_per_serving': 3.0,
                'carbs_per_serving': 8.0,
                'fat_per_serving': 5.0,
                'ayurvedic_benefits': 'Cooling, nourishing, good for Pitta and Vata',
                'best_time_to_eat': 'Morning or evening',
                'seasonal_notes': 'Excellent in summer, cooling and hydrating',
                'dosha_considerations': 'Pacifies Pitta and Vata, moderate for Kapha',
                'cooking_tips': 'Soak almonds longer for creamier texture',
                'variations': 'Add dates or cinnamon for different flavors',
                'storage_instructions': 'Refrigerate and shake before use'
            },
            {
                'food_name': 'Aloo Gobi',
                'recipe_name': 'Traditional Aloo Gobi',
                'description': 'Classic Indian potato and cauliflower curry',
                'ingredients': [
                    {'name': 'Potatoes', 'quantity': '2 medium'},
                    {'name': 'Cauliflower', 'quantity': '1 small head'},
                    {'name': 'Onion', 'quantity': '1 medium'},
                    {'name': 'Tomato', 'quantity': '2 medium'},
                    {'name': 'Ginger', 'quantity': '1 inch piece'},
                    {'name': 'Garlic', 'quantity': '3 cloves'},
                    {'name': 'Turmeric', 'quantity': '1/2 tsp'},
                    {'name': 'Cumin Seeds', 'quantity': '1 tsp'},
                    {'name': 'Coriander Powder', 'quantity': '1 tsp'},
                    {'name': 'Garam Masala', 'quantity': '1/2 tsp'},
                    {'name': 'Oil', 'quantity': '2 tbsp'},
                    {'name': 'Salt', 'quantity': 'to taste'},
                ],
                'instructions': [
                    'Cut potatoes and cauliflower into bite-sized pieces',
                    'Heat oil and add cumin seeds',
                    'Add chopped onions and cook until golden',
                    'Add ginger-garlic paste and cook for 1 minute',
                    'Add tomatoes and spices, cook until oil separates',
                    'Add potatoes and cauliflower, mix well',
                    'Cover and cook on low heat for 15-20 minutes',
                    'Garnish with fresh coriander leaves'
                ],
                'cooking_time': 'moderate',
                'difficulty': 'medium',
                'servings': 4,
                'calories_per_serving': 180,
                'protein_per_serving': 6.0,
                'carbs_per_serving': 35.0,
                'fat_per_serving': 4.0,
                'ayurvedic_benefits': 'Digestive, warming, good for Vata constitution',
                'best_time_to_eat': 'Lunch or dinner',
                'seasonal_notes': 'Good for all seasons, warming in winter',
                'dosha_considerations': 'Pacifies Vata, moderate for Pitta, avoid excess for Kapha',
                'cooking_tips': 'Don\'t overcook cauliflower to maintain texture',
                'variations': 'Add peas or bell peppers for extra nutrition',
                'storage_instructions': 'Refrigerate for up to 3 days, reheat before serving'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for recipe_data in sample_recipes:
            try:
                # Find the food
                food = Food.objects.get(name=recipe_data['food_name'])
                
                # Create or update recipe
                recipe, created = Recipe.objects.get_or_create(
                    name=recipe_data['recipe_name'],
                    food=food,
                    defaults={
                        'description': recipe_data['description'],
                        'ingredients': recipe_data['ingredients'],
                        'instructions': recipe_data['instructions'],
                        'cooking_time': recipe_data['cooking_time'],
                        'difficulty': recipe_data['difficulty'],
                        'servings': recipe_data['servings'],
                        'calories_per_serving': recipe_data['calories_per_serving'],
                        'protein_per_serving': recipe_data['protein_per_serving'],
                        'carbs_per_serving': recipe_data['carbs_per_serving'],
                        'fat_per_serving': recipe_data['fat_per_serving'],
                        'ayurvedic_benefits': recipe_data['ayurvedic_benefits'],
                        'best_time_to_eat': recipe_data['best_time_to_eat'],
                        'seasonal_notes': recipe_data['seasonal_notes'],
                        'dosha_considerations': recipe_data['dosha_considerations'],
                        'cooking_tips': recipe_data['cooking_tips'],
                        'variations': recipe_data['variations'],
                        'storage_instructions': recipe_data['storage_instructions'],
                        'created_by': user,
                        'is_active': True,
                        'is_public': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'Created recipe: {recipe.name}')
                else:
                    updated_count += 1
                    self.stdout.write(f'Updated recipe: {recipe.name}')
                    
            except Food.DoesNotExist:
                self.stdout.write(f'Food not found: {recipe_data["food_name"]}')
            except Exception as e:
                self.stdout.write(f'Error creating recipe for {recipe_data["food_name"]}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(sample_recipes)} recipes. '
                f'Created: {created_count}, Updated: {updated_count}'
            )
        )
