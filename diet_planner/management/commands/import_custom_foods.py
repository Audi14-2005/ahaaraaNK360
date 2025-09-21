import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from diet_planner.models import Food


class Command(BaseCommand):
    help = 'Import foods from custom CSV format'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing food data'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing foods before importing'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        # Check if file exists
        if not os.path.exists(csv_file):
            raise CommandError(f'CSV file "{csv_file}" does not exist.')
        
        # Clear existing foods if requested
        if options['clear']:
            Food.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing foods from database.')
            )
        
        imported_count = 0
        error_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
                    try:
                        # Map your CSV format to our database format
                        food_data = {
                            'name': row.get('name', '').strip(),
                            'category': row.get('food_cate', 'unknown').strip(),
                            'subcategory': row.get('meal_type', '').strip() or None,
                            'calories': self._safe_float(row.get('calories', 0)),
                            'protein': self._safe_float(row.get('protein_g', 0)),
                            'carbohydrates': self._safe_float(row.get('carbohydr', 0)),
                            'fat': self._safe_float(row.get('fat_g', 0)),
                            'fiber': 0.0,  # Default value since not in your CSV
                            'primary_taste': self._map_rasa(row.get('rasa', 'sweet')),
                            'secondary_taste': None,  # Not in your CSV
                            'energy': self._map_virya(row.get('virya', 'neutral')),
                            'vata_effect': self._map_dosha_effect(row.get('vata_effec', 'neutral')),
                            'pitta_effect': self._map_dosha_effect(row.get('pitta_effe', 'neutral')),
                            'kapha_effect': self._map_dosha_effect(row.get('kapha_eff', 'neutral')),
                            'is_vegetarian': True,  # Default
                            'is_vegan': True,  # Default
                            'is_gluten_free': True,  # Default
                            'is_dairy_free': True,  # Default
                            'contains_nuts': False,  # Default
                            'contains_soy': False,  # Default
                            'contains_eggs': False,  # Default
                            'contains_fish': False,  # Default
                            'contains_shellfish': False,  # Default
                        }
                        
                        # Create or update food
                        food, created = Food.objects.get_or_create(
                            name=food_data['name'],
                            defaults=food_data
                        )
                        
                        if created:
                            imported_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Imported: {food.name}')
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'⚠ Already exists: {food.name}')
                            )
                            
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'✗ Error on row {row_num}: {str(e)}')
                        )
                        continue
        
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Import completed!')
        )
        self.stdout.write(f'✓ Successfully imported: {imported_count} foods')
        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠ Errors encountered: {error_count} rows')
            )
        
        total_foods = Food.objects.count()
        self.stdout.write(f'📊 Total foods in database: {total_foods}')
        
        if imported_count > 0:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Foods are ready for AI diet planning!')
            )
    
    def _safe_float(self, value):
        """Safely convert string to float"""
        try:
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _map_rasa(self, rasa):
        """Map rasa to our taste choices"""
        rasa_mapping = {
            'sweet': 'sweet',
            'sour': 'sour',
            'salty': 'salty',
            'pungent': 'pungent',
            'bitter': 'bitter',
            'astringent': 'astringent',
        }
        return rasa_mapping.get(rasa.lower(), 'sweet')
    
    def _map_virya(self, virya):
        """Map virya to our energy choices"""
        virya_mapping = {
            'hot': 'heating',
            'cold': 'cooling',
            'warm': 'heating',
            'cool': 'cooling',
            'neutral': 'neutral',
        }
        return virya_mapping.get(virya.lower(), 'neutral')
    
    def _map_dosha_effect(self, effect):
        """Map dosha effect to our choices"""
        effect_mapping = {
            'increase': 'aggravates',
            'decrease': 'pacifies',
            'balance': 'neutral',
            'neutral': 'neutral',
            'pacify': 'pacifies',
            'aggravate': 'aggravates',
        }
        return effect_mapping.get(effect.lower(), 'neutral')


