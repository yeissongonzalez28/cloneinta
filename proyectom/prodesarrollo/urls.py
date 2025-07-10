from django.contrib import admin
from django.urls import path
from . import views
from .api_views import FeedListAPIView, ProfileDetailAPIView

urlpatterns = [
    path('', views.index, name='index'),
    path('registro', views.registro, name='registro'),
    path('inicio', views.inicio, name='inicio'),
    path('api/feed/', FeedListAPIView.as_view(), name='api-feed'),
    path('api/profile/<str:user__username>/', ProfileDetailAPIView.as_view(), name='api-profile'),
]