from django.core.management.base import BaseCommand
from food_scanner.models import FoodScan

class Command(BaseCommand):
    help = 'Update scan data with demo values'

    def handle(self, *args, **options):
        # Get all scans
        scans = FoodScan.objects.all()
        
        if not scans.exists():
            self.stdout.write(self.style.WARNING('No scans found in database'))
            return
        
        for scan in scans:
            self.stdout.write(f'Updating scan: {scan.id}')
            
            # Update with demo data
            scan.status = 'completed'
            scan.detected_food = 'Biryani Rice with Chicken'
            scan.confidence_score = 0.85
            
            # Nutritional data
            scan.calories = 250.0
            scan.protein = 15.0
            scan.carbohydrates = 30.0
            scan.fat = 8.0
            scan.fiber = 5.0
            scan.sugar = 12.0
            
            # Ayurvedic properties
            scan.rasa = 'sweet, sour'
            scan.virya = 'heating'
            scan.vipaka = 'sweet'
            scan.guna = 'light, dry'
            
            # Dosha effects
            scan.vata_effect = 'pacifies'
            scan.pitta_effect = 'neutral'
            scan.kapha_effect = 'aggravates'
            
            # Descriptions
            scan.ayurvedic_description = 'This food item has heating properties and is beneficial for Vata dosha. It should be consumed in moderation by Kapha types.'
            scan.recommendations = 'Best consumed during lunch time. Pair with cooling foods for balance.'
            scan.warnings = 'May aggravate Pitta if consumed in excess.'
            
            scan.save()
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {scans.count()} scans'))


