"""
Food Scanner URLs
"""
from django.urls import path
from . import views

app_name = 'food_scanner'

urlpatterns = [
    # Main pages
    path('', views.scanner_dashboard, name='dashboard'),
    path('scan/', views.scan_food, name='scan_food'),
    path('scans/', views.scan_list, name='scan_list'),
    path('scans/<uuid:scan_id>/', views.scan_detail, name='scan_detail'),
    path('scans/<uuid:scan_id>/delete/', views.delete_scan, name='delete_scan'),
    
    # Food database
    path('database/', views.food_database, name='food_database'),
    path('database/<uuid:food_id>/', views.food_detail, name='food_detail'),
    path('database/import-csv/', views.import_foods_csv, name='import_foods_csv'),
    
    # API endpoints
    path('api/scan/', views.api_scan_food, name='api_scan_food'),
]
