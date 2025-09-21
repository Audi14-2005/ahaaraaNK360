"""
Management command to update dosha effects for existing foods
"""
from django.core.management.base import BaseCommand
from diet_planner.models import Food
import csv
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Update dosha effects for existing foods from CSV data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            help='Path to CSV file with dosha effect data',
        )
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Clear all existing foods before importing',
        )

    def handle(self, *args, **options):
        csv_file_path = options.get('csv_file')
        
        if not csv_file_path:
            self.stdout.write(
                self.style.ERROR('Please provide --csv-file argument')
            )
            return

        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file_path}')
            )
            return

        if options['clear_all']:
            Food.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Cleared all existing foods')
            )

        # Import the mapping functions from views
        def safe_float(value):
            try:
                return float(value) if value else 0.0
            except (ValueError, TypeError):
                return 0.0

        def map_rasa(rasa):
            if not rasa or rasa.strip() == '':
                return 'sweet'
            
            rasa = rasa.lower().strip()
            rasa_mapping = {
                'sweet': 'sweet', 'sweetness': 'sweet', 'madhura': 'sweet',
                'sour': 'sour', 'sourness': 'sour', 'amla': 'sour',
                'salty': 'salty', 'salt': 'salty', 'lavana': 'salty',
                'pungent': 'pungent', 'spicy': 'pungent', 'katu': 'pungent', 'hot': 'pungent',
                'bitter': 'bitter', 'bitterness': 'bitter', 'tikta': 'bitter',
                'astringent': 'astringent', 'kashaya': 'astringent', 'dry': 'astringent',
            }
            return rasa_mapping.get(rasa, 'sweet')

        def map_virya(virya):
            if not virya or virya.strip() == '':
                return 'neutral'
            
            virya = virya.lower().strip()
            virya_mapping = {
                'hot': 'heating', 'heating': 'heating', 'warm': 'heating', 'ushna': 'heating',
                'cold': 'cooling', 'cooling': 'cooling', 'cool': 'cooling', 'sheeta': 'cooling',
                'neutral': 'neutral', 'moderate': 'neutral', 'balanced': 'neutral',
            }
            return virya_mapping.get(virya, 'neutral')

        def map_dosha_effect(effect):
            if not effect or effect.strip() == '':
                return 'neutral'
            
            effect = effect.lower().strip()
            effect_mapping = {
                # Aggravates/Increases
                'increase': 'aggravates', 'aggravate': 'aggravates', 'aggravates': 'aggravates',
                'high': 'aggravates', 'strong': 'aggravates', 'excess': 'aggravates',
                'worsen': 'aggravates', 'worsens': 'aggravates', 'intensify': 'aggravates',
                
                # Pacifies/Decreases
                'decrease': 'pacifies', 'pacify': 'pacifies', 'pacifies': 'pacifies',
                'low': 'pacifies', 'reduce': 'pacifies', 'reduces': 'pacifies',
                'balance': 'pacifies', 'balances': 'pacifies', 'calm': 'pacifies',
                'soothe': 'pacifies', 'soothes': 'pacifies', 'alleviate': 'pacifies',
                
                # Neutral
                'neutral': 'neutral', 'moderate': 'neutral', 'normal': 'neutral',
                'balanced': 'neutral', 'stable': 'neutral', 'mild': 'neutral',
            }
            return effect_mapping.get(effect, 'neutral')

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                imported_count = 0
                updated_count = 0
                error_count = 0
                
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        food_data = {
                            'name': row.get('name', '').strip(),
                            'category': row.get('food_cate', 'unknown').strip(),
                            'subcategory': row.get('meal_type', '').strip() or None,
                            'calories': safe_float(row.get('calories', 0)),
                            'protein': safe_float(row.get('protein_g', 0)),
                            'carbohydrates': safe_float(row.get('carbohydr', 0)),
                            'fat': safe_float(row.get('fat_g', 0)),
                            'fiber': 0.0,  # Default value
                            'primary_taste': map_rasa(row.get('rasa', 'sweet')),
                            'secondary_taste': None,
                            'energy': map_virya(row.get('virya', 'neutral')),
                            'vata_effect': map_dosha_effect(row.get('vata_effec', 'neutral')),
                            'pitta_effect': map_dosha_effect(row.get('pitta_effe', 'neutral')),
                            'kapha_effect': map_dosha_effect(row.get('kapha_eff', 'neutral')),
                            'is_vegetarian': True,
                            'is_vegan': True,
                            'is_gluten_free': True,
                            'is_dairy_free': True,
                            'contains_nuts': False,
                            'contains_soy': False,
                            'contains_eggs': False,
                            'contains_fish': False,
                            'contains_shellfish': False,
                        }
                        
                        # Create or update food
                        food, created = Food.objects.get_or_create(
                            name=food_data['name'],
                            defaults=food_data
                        )
                        
                        if not created:
                            # Update existing food with new dosha effects
                            food.vata_effect = food_data['vata_effect']
                            food.pitta_effect = food_data['pitta_effect']
                            food.kapha_effect = food_data['kapha_effect']
                            food.primary_taste = food_data['primary_taste']
                            food.energy = food_data['energy']
                            food.calories = food_data['calories']
                            food.protein = food_data['protein']
                            food.carbohydrates = food_data['carbohydrates']
                            food.fat = food_data['fat']
                            food.save()
                            updated_count += 1
                        else:
                            imported_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Error processing row {row_num}: {str(e)}')
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Import completed: {imported_count} new foods, '
                        f'{updated_count} updated, {error_count} errors'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading CSV file: {str(e)}')
            )


