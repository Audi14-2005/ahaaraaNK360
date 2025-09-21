from django.core.management.base import BaseCommand
from diet_planner.models import Food
from food_scanner.models import FoodDatabase

class Command(BaseCommand):
    help = 'Sync food data from FoodScanner to DietPlanner'

    def handle(self, *args, **options):
        # Get all foods from food scanner database
        food_scanner_foods = FoodDatabase.objects.all()
        
        synced_count = 0
        updated_count = 0
        
        for fs_food in food_scanner_foods:
            # Map food scanner fields to diet planner fields
            food_data = {
                'name': fs_food.name,
                'category': fs_food.category or 'other',
                'calories': int(fs_food.calories),
                'protein': fs_food.protein,
                'carbohydrates': fs_food.carbohydrates,
                'fat': fs_food.fat,
                'fiber': fs_food.fiber,
                'primary_taste': self.map_taste(fs_food.primary_taste),
                'energy': self.map_energy(fs_food.energy),
                'vata_effect': self.map_dosha_effect(fs_food.vata_effect),
                'pitta_effect': self.map_dosha_effect(fs_food.pitta_effect),
                'kapha_effect': self.map_dosha_effect(fs_food.kapha_effect),
            }
            
            # Create or update food in diet planner
            food, created = Food.objects.get_or_create(
                name=fs_food.name,
                defaults=food_data
            )
            
            if created:
                synced_count += 1
                self.stdout.write(f'✅ Created: {fs_food.name}')
            else:
                # Update existing food
                for key, value in food_data.items():
                    setattr(food, key, value)
                food.save()
                updated_count += 1
                self.stdout.write(f'🔄 Updated: {fs_food.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully synced {synced_count} new foods and updated {updated_count} existing foods!'
            )
        )

    def map_taste(self, taste):
        """Map taste values between models"""
        if not taste:
            return 'sweet'
        
        taste = taste.lower().strip()
        taste_mapping = {
            'sweet': 'sweet',
            'sour': 'sour',
            'salty': 'salty',
            'pungent': 'pungent',
            'bitter': 'bitter',
            'astringent': 'astringent',
        }
        return taste_mapping.get(taste, 'sweet')

    def map_energy(self, energy):
        """Map energy values between models"""
        if not energy:
            return 'neutral'
        
        energy = energy.lower().strip()
        energy_mapping = {
            'heating': 'heating',
            'cooling': 'cooling',
            'neutral': 'neutral',
        }
        return energy_mapping.get(energy, 'neutral')

    def map_dosha_effect(self, effect):
        """Map dosha effect values between models"""
        if not effect:
            return 'neutral'
        
        effect = effect.lower().strip()
        effect_mapping = {
            'pacifies': 'pacifies',
            'aggravates': 'aggravates',
            'neutral': 'neutral',
        }
        return effect_mapping.get(effect, 'neutral')

