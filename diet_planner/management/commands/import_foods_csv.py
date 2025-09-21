import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from diet_planner.models import Food


class Command(BaseCommand):
    help = 'Import foods from a CSV file'

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
                        # Convert string boolean values to actual booleans
                        def str_to_bool(value):
                            if isinstance(value, str):
                                return value.lower() in ('true', '1', 'yes', 'on')
                            return bool(value)
                        
                        # Handle empty secondary_taste
                        secondary_taste = row.get('secondary_taste', '').strip()
                        if not secondary_taste:
                            secondary_taste = None
                        
                        food_data = {
                            'name': row['name'].strip(),
                            'category': row['category'].strip(),
                            'subcategory': row.get('subcategory', '').strip() or None,
                            'calories': int(float(row['calories'])),
                            'protein': float(row['protein']),
                            'carbohydrates': float(row['carbohydrates']),
                            'fat': float(row['fat']),
                            'fiber': float(row['fiber']),
                            'primary_taste': row['primary_taste'].strip(),
                            'secondary_taste': secondary_taste,
                            'energy': row['energy'].strip(),
                            'vata_effect': row['vata_effect'].strip(),
                            'pitta_effect': row['pitta_effect'].strip(),
                            'kapha_effect': row['kapha_effect'].strip(),
                            'is_vegetarian': str_to_bool(row.get('is_vegetarian', 'True')),
                            'is_vegan': str_to_bool(row.get('is_vegan', 'True')),
                            'is_gluten_free': str_to_bool(row.get('is_gluten_free', 'True')),
                            'is_dairy_free': str_to_bool(row.get('is_dairy_free', 'True')),
                            'contains_nuts': str_to_bool(row.get('contains_nuts', 'False')),
                            'contains_soy': str_to_bool(row.get('contains_soy', 'False')),
                            'contains_eggs': str_to_bool(row.get('contains_eggs', 'False')),
                            'contains_fish': str_to_bool(row.get('contains_fish', 'False')),
                            'contains_shellfish': str_to_bool(row.get('contains_shellfish', 'False')),
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


