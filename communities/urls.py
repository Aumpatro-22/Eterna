from django.urls import path
from . import views

app_name = 'communities'

urlpatterns = [
    path('', views.community_list, name='list'),
    path('create/', views.community_create, name='create'),
    path('<slug:slug>/', views.community_detail, name='detail'),
    path('<slug:slug>/join/', views.join_community, name='join'),
    path('<slug:slug>/leave/', views.leave_community, name='leave'),
    path('<slug:slug>/c/<slug:channel_slug>/post/', views.post_message, name='post_message'),
    path('<slug:slug>/c/<slug:channel_slug>/feed/', views.messages_feed, name='messages_feed'),
]
