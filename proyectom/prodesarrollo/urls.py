from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registro', views.registro_usuario, name='registro'),
    path('inicio', views.inicio, name='inicio'),
    path('verificar', views.verificar_codigo, name='verificar'),
    path('reenviar', views.reenviar_codigo, name='reenviar_codigo'),
]