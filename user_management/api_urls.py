from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserProfileViewSet, PatientProfileViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'patient-profiles', PatientProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

