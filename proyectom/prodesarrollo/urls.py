from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('', LogoutView.as_view(next_page='index'), name='cerrarse'),
    path('registro', views.registro_usuario, name='registro'),
    path('inicio', views.inicio, name='inicio'),
    path('verificar', views.verificar_codigo, name='verificar'),
    path('reenviar', views.reenviar_codigo, name='reenviar_codigo'),
    path('mensajes', views.mensajes, name='mensajes'),
    path('seguir/<str:nombre_usuario>/', views.seguir_usuario, name='seguir_usuario'),
    path('sugerencias/todas/', views.ver_todas_sugerencias, name='ver_todas_sugerencias'),
    path('perfil/<str:username>/', views.perfil, name='perfil'),
    path('editar_perfil', views.editar_perfil, name='editar_perfil'),
    path('crear/', views.crear_publicacion, name='crear_publicacion'),
    path('<str:username>/', views.chat, name='chat'),
]