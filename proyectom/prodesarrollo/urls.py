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
    path('mensajes/', views.mensajes, name='mensajes'),
    path('seguir/<str:nombre_usuario>/', views.seguir_usuario, name='seguir_usuario'),
    path('sugerencias/todas/', views.ver_todas_sugerencias, name='ver_todas_sugerencias'),
    path('perfil/<str:username>/', views.perfil, name='perfil'),
    path('editar_perfil', views.editar_perfil, name='editar_perfil'),
    path('crear/', views.crear_publicacion, name='crear_publicacion'),
    path('mensajes/', views.mensajes, name='mensajes'),  # Para ver a quién sigues
    path('mensajes/<str:username>/', views.chat, name='chat'),
    path('enviar_mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    path('obtener_mensajes/<str:username>/', views.obtener_mensajes, name='obtener_mensajes'),
    path('buscar_usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('crear_historia/', views.crear_historia, name='crear_historia'),
    path('obtener_historias/', views.obtener_historias, name='obtener_historias'),
    path('obtener_historia/<int:historia_id>/', views.obtener_historia, name='obtener_historia'),
    path('obtener_historias/<int:historia_id>/usuario/', views.obtener_historias_usuario, name='obtener_historias_usuario'),
    path('obtener_todas_historias/', views.obtener_todas_historias, name='obtener_todas_historias'),
    path('reels/', views.reels, name='reels'),
]