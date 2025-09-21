from django.urls import path
from . import views

app_name = 'diet_planner'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Patient Management
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<uuid:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/<uuid:patient_id>/debug/', views.debug_patient, name='debug_patient'),
    path('patients/create/', views.create_patient, name='create_patient'),
    
    # Diet Chart Management
    path('patients/<uuid:patient_id>/generate-chart/', views.generate_diet_chart, name='generate_diet_chart'),
    path('charts/<uuid:chart_id>/', views.diet_chart_detail, name='diet_chart_detail'),
    path('charts/<uuid:chart_id>/edit/', views.edit_diet_chart, name='edit_diet_chart'),
    
    # AI Food Swapping
    path('api/meal-items/<uuid:meal_item_id>/similar-foods/', views.get_similar_foods, name='get_similar_foods'),
    path('api/meal-items/<uuid:meal_item_id>/swap/', views.swap_food, name='swap_food'),
    
    # Food Database
    path('foods/', views.food_database, name='food_database'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    path('import-foods/', views.import_foods_csv, name='import_foods_csv'),
    path('import-custom-foods/', views.import_custom_foods_csv, name='import_custom_foods_csv'),
    path('download-sample-csv/', views.download_sample_csv, name='download_sample_csv'),
    
    # Recipe Management
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/<uuid:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('foods/<uuid:food_id>/recipes/', views.food_recipes, name='food_recipes'),
    path('charts/<uuid:chart_id>/with-recipes/', views.diet_chart_with_recipes, name='diet_chart_with_recipes'),
    path('foods/<uuid:food_id>/generate-recipe/', views.generate_recipe_chat, name='generate_recipe_chat'),
    path('foods/<uuid:food_id>/generate-recipe-ai/', views.generate_recipe_ai, name='generate_recipe_ai'),
]

