from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('edit/<int:pk>/', views.edit_post, name='edit_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
]


