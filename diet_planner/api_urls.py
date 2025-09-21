from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    FoodViewSet, PatientViewSet, DietChartViewSet, 
    RecipeViewSet, MealPlanViewSet, MealItemViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'foods', FoodViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'diet-charts', DietChartViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'meal-plans', MealPlanViewSet)
router.register(r'meal-items', MealItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
