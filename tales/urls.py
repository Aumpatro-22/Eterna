from django.urls import path
from . import views

app_name = 'tales'

urlpatterns = [
    path('', views.tale_list, name='list'),
    path('create/', views.tale_create, name='create'),
    path('<slug:slug>/chapters/add/', views.chapter_create, name='chapter_create'),
    path('<slug:slug>/chapters/<int:chapter_id>/publish/', views.chapter_publish, name='chapter_publish'),  # NEW
    path('<slug:slug>/delete/', views.tale_delete, name='delete'),  # NEW
    path('<slug:slug>/', views.tale_detail, name='detail'),
]
