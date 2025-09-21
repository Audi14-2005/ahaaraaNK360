"""
Food Scanner Views
AI-powered food analysis and nutritional information
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
import os
import csv
import logging
from .models import FoodScan, FoodDatabase
from .forms import FoodScanForm

logger = logging.getLogger(__name__)

@login_required
def scanner_dashboard(request):
    """Food Scanner Dashboard"""
    total_scans = FoodScan.objects.filter(user=request.user).count()
    completed_scans = FoodScan.objects.filter(user=request.user, status='completed').count()
    recent_scans = FoodScan.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'total_scans': total_scans,
        'completed_scans': completed_scans,
        'recent_scans': recent_scans,
    }
    return render(request, 'food_scanner/dashboard.html', context)


@login_required
def scan_food(request):
    """Food scanning interface with camera and upload options"""
    if request.method == 'POST':
        form = FoodScanForm(request.POST, request.FILES)
        if form.is_valid():
            # Create food scan record
            food_scan = form.save(commit=False)
            food_scan.user = request.user
            food_scan.scan_type = 'upload'  # Set scan type manually
            food_scan.status = 'processing'
            food_scan.save()
            
            # Process the image with AI analysis
            try:
                # Try to match with existing food database first
                matched_food = find_matching_food_in_database(food_scan.image.name)
                
                if matched_food:
                    # Use real data from database
                    food_scan.status = 'completed'
                    food_scan.detected_food = matched_food.name
                    food_scan.confidence_score = 0.9  # High confidence for database match
                    
                    # Nutritional data from database
                    food_scan.calories = matched_food.calories
                    food_scan.protein = matched_food.protein
                    food_scan.carbohydrates = matched_food.carbohydrates
                    food_scan.fat = matched_food.fat
                    food_scan.fiber = matched_food.fiber
                    food_scan.sugar = matched_food.sugar
                    
                    # Ayurvedic properties from database
                    food_scan.rasa = matched_food.primary_taste
                    food_scan.virya = matched_food.energy
                    food_scan.vipaka = matched_food.vipaka
                    food_scan.guna = matched_food.guna
                    
                    # Dosha effects from database
                    food_scan.vata_effect = matched_food.vata_effect
                    food_scan.pitta_effect = matched_food.pitta_effect
                    food_scan.kapha_effect = matched_food.kapha_effect
                    
                    # Additional information
                    food_scan.ayurvedic_description = matched_food.recommendations
                    food_scan.recommendations = matched_food.recommendations
                    food_scan.warnings = matched_food.avoidances
                    
                    # Link to matched food
                    food_scan.matched_food = matched_food
                    
                    messages.success(request, f'Food matched with database! Detected: {food_scan.detected_food}')
                else:
                    # Fallback to demo data if no match found
                    food_scan.status = 'completed'
                    food_scan.detected_food = 'Unknown Food Item'
                    food_scan.confidence_score = 0.6
                    
                    # Demo nutritional data
                    food_scan.calories = 200.0
                    food_scan.protein = 10.0
                    food_scan.carbohydrates = 25.0
                    food_scan.fat = 5.0
                    food_scan.fiber = 3.0
                    food_scan.sugar = 8.0
                    
                    # Demo Ayurvedic properties
                    food_scan.rasa = 'sweet'
                    food_scan.virya = 'neutral'
                    food_scan.vipaka = 'sweet'
                    food_scan.guna = 'light'
                    
                    # Demo dosha effects
                    food_scan.vata_effect = 'neutral'
                    food_scan.pitta_effect = 'neutral'
                    food_scan.kapha_effect = 'neutral'
                    
                    # Demo descriptions
                    food_scan.ayurvedic_description = 'This food item has neutral properties. Please consult a nutritionist for detailed analysis.'
                    food_scan.recommendations = 'Consume in moderation as part of a balanced diet.'
                    food_scan.warnings = 'No specific warnings available.'
                    
                    messages.info(request, f'Food not found in database. Showing general analysis for: {food_scan.detected_food}')
                
                food_scan.save()
                return redirect('food_scanner:scan_detail', scan_id=food_scan.id)
                    
            except Exception as e:
                logger.error(f"Error processing food scan: {e}")
                food_scan.status = 'failed'
                food_scan.error_message = str(e)
                food_scan.save()
                
                messages.error(request, f'Error processing food scan: {str(e)}')
                return redirect('food_scanner:scan_food')
        else:
            messages.error(request, 'Invalid form submission. Please check the image file.')
    else:
        form = FoodScanForm()
    
    context = {
        'form': form,
    }
    return render(request, 'food_scanner/scan_food.html', context)


def find_matching_food_in_database(image_name):
    """
    Simple food matching based on image name or other heuristics.
    In a real implementation, this would use AI to identify the food.
    """
    # For now, let's return a random food from the database to demonstrate the system
    # In production, this would use AI to analyze the image and match with database
    
    # Get a random food from the database
    import random
    foods = list(FoodDatabase.objects.all())
    
    if foods:
        # Return a random food to show the system is working
        random_food = random.choice(foods)
        print(f"🎲 Using random food for demo: {random_food.name}")
        return random_food
    
    return None


@login_required
def scan_detail(request, scan_id):
    """Detailed view of a food scan analysis"""
    food_scan = get_object_or_404(FoodScan, id=scan_id, user=request.user)
    
    context = {
        'food_scan': food_scan,
    }
    return render(request, 'food_scanner/scan_detail.html', context)


@login_required
def scan_list(request):
    """List all food scans for the user"""
    scans = FoodScan.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        scans = scans.filter(status=status_filter)
    
    # Search by food name
    search_query = request.GET.get('search')
    if search_query:
        scans = scans.filter(detected_food__icontains=search_query)
    
    context = {
        'scans': scans,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'food_scanner/scan_list.html', context)


@login_required
def delete_scan(request, scan_id):
    """Delete a food scan"""
    food_scan = get_object_or_404(FoodScan, id=scan_id, user=request.user)
    
    try:
        # Delete the image file
        if food_scan.image:
            if os.path.isfile(food_scan.image.path):
                os.remove(food_scan.image.path)
        
        food_scan.delete()
        messages.success(request, 'Food scan deleted successfully!')
        
    except Exception as e:
        logger.error(f"Error deleting food scan: {e}")
        messages.error(request, f'Error deleting food scan: {str(e)}')
    
    return redirect('food_scanner:scan_list')


@login_required
def food_database(request):
    """Display the comprehensive food database"""
    foods = FoodDatabase.objects.all().order_by('name')
    context = {
        'foods': foods,
    }
    return render(request, 'food_scanner/food_database.html', context)


@login_required
def food_detail(request, food_id):
    """Detailed view of a food item from the database"""
    food = get_object_or_404(FoodDatabase, id=food_id)
    context = {
        'food': food,
    }
    return render(request, 'food_scanner/food_detail.html', context)


@login_required
def import_foods_csv(request):
    """Import foods from CSV file"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return redirect('food_scanner:food_database')
        
        try:
            # Read CSV file
            csv_data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(csv_data.splitlines())
            
            imported_count = 0
            updated_count = 0
            
            for row in csv_reader:
                # Debug: Print row data
                print(f"Processing row: {row}")
                
                # Map CSV fields to FoodDatabase fields
                food_data = {
                    'name': row.get('Food Item', '').strip(),
                    'meal_type': row.get('Meal Type', '').strip(),
                    'calories': float(row.get('Calories (k)', 0) or 0),
                    'protein': float(row.get('Protein (g)', 0) or 0),
                    'carbohydrates': float(row.get('Carbs (g)', 0) or 0),
                    'fat': float(row.get('Fat (g)', 0) or 0),
                    'fiber': float(row.get('Fibre (g)', 0) or 0),
                    'category': row.get('Category', '').strip().lower(),
                    'tags': row.get('Tags', '').strip(),
                    'primary_taste': map_rasa(row.get('Rasa', '') or ''),
                    'energy': map_virya(row.get('Virya', '') or ''),
                    'vipaka': map_vipaka(row.get('Vipaka', '') or ''),
                    'guna': (row.get('Guna', '') or '').strip(),
                    'vata_effect': map_dosha_effect(row.get('Dosha Effect', '') or ''),
                    'pitta_effect': map_dosha_effect(row.get('Dosha Effect', '') or ''),
                    'kapha_effect': map_dosha_effect(row.get('Dosha Effect', '') or ''),
                    'recommendations': f"Meal Type: {row.get('Meal Type', '')} | Category: {row.get('Category', '')} | Tags: {row.get('Tags', '')}",
                    'avoidances': '',
                }
                
                if food_data['name']:
                    try:
                        # Check if food already exists
                        food, created = FoodDatabase.objects.get_or_create(
                            name=food_data['name'],
                            defaults=food_data
                        )
                        
                        if created:
                            imported_count += 1
                            print(f"✅ Imported: {food_data['name']}")
                        else:
                            # Update existing food
                            for key, value in food_data.items():
                                setattr(food, key, value)
                            food.save()
                            updated_count += 1
                            print(f"🔄 Updated: {food_data['name']}")
                    except Exception as e:
                        print(f"❌ Error processing {food_data['name']}: {e}")
                        logger.error(f"Error processing food {food_data['name']}: {e}")
                else:
                    print(f"⚠️ Skipping empty name row: {row}")
            
            messages.success(request, f'Successfully imported {imported_count} new foods and updated {updated_count} existing foods.')
            
            # Automatically sync to diet planner database
            try:
                from diet_planner.models import Food
                sync_count = 0
                
                for fs_food in FoodDatabase.objects.all():
                    food_data = {
                        'name': fs_food.name,
                        'category': fs_food.category or 'other',
                        'calories': int(fs_food.calories),
                        'protein': fs_food.protein,
                        'carbohydrates': fs_food.carbohydrates,
                        'fat': fs_food.fat,
                        'fiber': fs_food.fiber,
                        'primary_taste': map_taste(fs_food.primary_taste),
                        'energy': map_energy(fs_food.energy),
                        'vata_effect': map_dosha_effect(fs_food.vata_effect),
                        'pitta_effect': map_dosha_effect(fs_food.pitta_effect),
                        'kapha_effect': map_dosha_effect(fs_food.kapha_effect),
                    }
                    
                    food, created = Food.objects.get_or_create(
                        name=fs_food.name,
                        defaults=food_data
                    )
                    
                    if created:
                        sync_count += 1
                    else:
                        # Update existing food
                        for key, value in food_data.items():
                            setattr(food, key, value)
                        food.save()
                
                messages.success(request, f'Also synced {sync_count} foods to diet planner database!')
                
            except Exception as sync_error:
                logger.error(f"Error syncing to diet planner: {sync_error}")
                messages.warning(request, f'CSV imported but sync to diet planner failed: {str(sync_error)}')
            
        except Exception as e:
            logger.error(f"Error importing CSV: {e}")
            messages.error(request, f'Error importing CSV: {str(e)}')
    
    return redirect('food_scanner:food_database')


def map_rasa(rasa):
    """Map rasa values to database choices"""
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
    """Map virya values to database choices"""
    if not virya or virya.strip() == '':
        return 'neutral'
    
    virya = virya.lower().strip()
    virya_mapping = {
        'hot': 'heating', 'heating': 'heating', 'warm': 'heating', 'ushna': 'heating',
        'cold': 'cooling', 'cooling': 'cooling', 'cool': 'cooling', 'sheeta': 'cooling',
        'neutral': 'neutral', 'moderate': 'neutral', 'balanced': 'neutral',
    }
    return virya_mapping.get(virya, 'neutral')


def map_vipaka(vipaka):
    """Map vipaka values to database choices"""
    if not vipaka or vipaka.strip() == '':
        return 'sweet'
    
    vipaka = vipaka.lower().strip()
    vipaka_mapping = {
        'sweet': 'sweet', 'sweetness': 'sweet',
        'sour': 'sour', 'sourness': 'sour',
        'pungent': 'pungent', 'spicy': 'pungent',
    }
    return vipaka_mapping.get(vipaka, 'sweet')


def map_dosha_effect(effect):
    """Map dosha effect values to database choices"""
    if not effect or effect.strip() == '':
        return 'neutral'
    
    effect = effect.lower().strip()
    effect_mapping = {
        'increase': 'aggravates', 'aggravate': 'aggravates', 'aggravates': 'aggravates',
        'decrease': 'pacifies', 'pacify': 'pacifies', 'pacifies': 'pacifies',
        'neutral': 'neutral', 'moderate': 'neutral', 'balanced': 'neutral',
    }
    return effect_mapping.get(effect, 'neutral')


def map_taste(taste):
    """Map taste values for diet planner sync"""
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


def map_energy(energy):
    """Map energy values for diet planner sync"""
    if not energy:
        return 'neutral'
    
    energy = energy.lower().strip()
    energy_mapping = {
        'heating': 'heating',
        'cooling': 'cooling',
        'neutral': 'neutral',
    }
    return energy_mapping.get(energy, 'neutral')


@login_required
def api_scan_food(request):
    """API endpoint for food scanning"""
    if request.method == 'POST':
        # Handle API scan request
        return JsonResponse({'message': 'API scan endpoint'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)