from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Patient, Food, DietChart, MealPlan, MealItem, Recipe
from .serializers import (
    PatientSerializer, FoodSerializer, DietChartSerializer, 
    MealPlanSerializer, MealItemSerializer, RecipeSerializer
)
from .services import DietArchitectAI, RecipeGeneratorAI
import logging

logger = logging.getLogger(__name__)


class FoodViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Food model - Read only for mobile app"""
    queryset = Food.objects.filter(is_active=True)
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def generate_recipe(self, request, pk=None):
        """Generate AI recipe for a specific food"""
        try:
            food = self.get_object()
            meal_type = request.data.get('meal_type', 'lunch')
            
            recipe_ai = RecipeGeneratorAI()
            result = recipe_ai.generate_recipe(food, meal_type, request.user)
            
            if result['success']:
                recipe = Recipe.objects.get(id=result['recipe_id'])
                serializer = RecipeSerializer(recipe)
                return Response({
                    'success': True,
                    'recipe': serializer.data,
                    'message': result['message']
                })
            else:
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for Patient model"""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return patients for the authenticated user"""
        if self.request.user.userprofile.user_type == 'dietitian':
            return Patient.objects.filter(dietitian=self.request.user)
        elif self.request.user.userprofile.user_type == 'patient':
            return Patient.objects.filter(user_profile__user=self.request.user)
        return Patient.objects.none()
    
    @action(detail=True, methods=['post'])
    def generate_diet_chart(self, request, pk=None):
        """Generate diet chart for a specific patient"""
        try:
            patient = self.get_object()
            duration_days = request.data.get('duration_days', 7)
            
            # Check if patient has required data
            if not patient.height or not patient.weight or not patient.age:
                return Response({
                    'success': False,
                    'error': 'Patient must have height, weight, and age to generate diet chart',
                    'missing_fields': {
                        'height': patient.height is None,
                        'weight': patient.weight is None,
                        'age': patient.age is None
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate diet chart using AI
            diet_ai = DietArchitectAI()
            result = diet_ai.generate_diet_chart(patient, duration_days)
            
            if result['success']:
                diet_chart = DietChart.objects.get(id=result['diet_chart_id'])
                serializer = DietChartSerializer(diet_chart)
                return Response({
                    'success': True,
                    'diet_chart': serializer.data,
                    'message': result['message']
                })
            else:
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error generating diet chart: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DietChartViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DietChart model - Read only for mobile app"""
    queryset = DietChart.objects.all()
    serializer_class = DietChartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return diet charts for the authenticated user"""
        if self.request.user.userprofile.user_type == 'dietitian':
            return DietChart.objects.filter(dietitian=self.request.user)
        elif self.request.user.userprofile.user_type == 'patient':
            return DietChart.objects.filter(patient__user_profile__user=self.request.user)
        return DietChart.objects.none()


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Recipe model - Read only for mobile app"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]


class MealPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for MealPlan model - Read only for mobile app"""
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return meal plans for the authenticated user"""
        if self.request.user.userprofile.user_type == 'dietitian':
            return MealPlan.objects.filter(diet_chart__dietitian=self.request.user)
        elif self.request.user.userprofile.user_type == 'patient':
            return MealPlan.objects.filter(diet_chart__patient__user_profile__user=self.request.user)
        return MealPlan.objects.none()


class MealItemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for MealItem model - Read only for mobile app"""
    queryset = MealItem.objects.all()
    serializer_class = MealItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return meal items for the authenticated user"""
        if self.request.user.userprofile.user_type == 'dietitian':
            return MealItem.objects.filter(meal_plan__diet_chart__dietitian=self.request.user)
        elif self.request.user.userprofile.user_type == 'patient':
            return MealItem.objects.filter(meal_plan__diet_chart__patient__user_profile__user=self.request.user)
        return MealItem.objects.none()
