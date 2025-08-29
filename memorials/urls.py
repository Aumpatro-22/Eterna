from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('memorial/<int:pk>/', views.MemorialDetailView.as_view(), name='memorial_detail'),
    path('memorial/create/', views.create_memorial, name='create_memorial'),
    path('memorial/<int:pk>/update/', views.update_memorial, name='update_memorial'),
    path('memorial/<int:pk>/delete/', views.delete_memorial, name='delete_memorial'),
    path('memorial/<int:memorial_pk>/message/', views.add_message, name='add_message'),
    path('memorial/<int:memorial_pk>/candle/', views.light_candle, name='light_candle'),
    path('m/<str:public_id>/', views.MemorialByIdView.as_view(), name='memorial_detail_by_id'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),  # NEW
    path('privacy/', views.privacy, name='privacy'),
]
