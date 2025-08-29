from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('search/', views.search_profiles, name='search_profiles'),
    path('react/', views.react, name='react'),  # NEW
    path('u/<str:username>/', views.profile_detail, name='profile'),  # NEW
    path('u/<str:username>/dm/', views.send_dm, name='send_dm'),  # NEW
]
