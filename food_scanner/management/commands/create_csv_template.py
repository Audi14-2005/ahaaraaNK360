from django.core.management.base import BaseCommand
import csv
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Create a CSV template file for food import'

    def handle(self, *args, **options):
        # Create the template CSV file
        template_path = os.path.join(settings.BASE_DIR, 'food_import_template.csv')
        
        # Sample data for the template
        sample_data = [
            {
                'Food Item': 'Sample Food 1',
                'Meal Type': 'Breakfast',
                'Calories (k)': '150',
                'Carbs (g)': '25',
                'Protein (g)': '8',
                'Fat (g)': '3',
                'Fibre (g)': '4',
                'Category': 'Grains',
                'Tags': 'healthy, organic',
                'Rasa': 'Sweet',
                'Virya': 'Neutral',
                'Vipaka': 'Sweet',
                'Guna': 'Light, Dry',
                'Dosha Effect': 'Neutral'
            },
            {
                'Food Item': 'Sample Food 2',
                'Meal Type': 'Lunch',
                'Calories (k)': '200',
                'Carbs (g)': '30',
                'Protein (g)': '12',
                'Fat (g)': '5',
                'Fibre (g)': '6',
                'Category': 'Vegetables',
                'Tags': 'fresh, green',
                'Rasa': 'Bitter',
                'Virya': 'Cooling',
                'Vipaka': 'Pungent',
                'Guna': 'Light, Cold',
                'Dosha Effect': 'Pacifies'
            }
        ]
        
        # Write the template CSV
        with open(template_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Food Item', 'Meal Type', 'Calories (k)', 'Carbs (g)', 'Protein (g)',
                'Fat (g)', 'Fibre (g)', 'Category', 'Tags', 'Rasa', 'Virya',
                'Vipaka', 'Guna', 'Dosha Effect'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'CSV template created at: {template_path}'
            )
        )
        self.stdout.write(
            'You can use this template as a reference for your CSV format.'
        )

