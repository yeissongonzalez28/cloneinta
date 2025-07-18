from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from uuid import uuid4
import os

class Usuario(AbstractUser):
    # ✅ Clave primaria personalizada
    username = models.CharField(
        max_length=50,
        unique=True,
        primary_key=True,  # <- Aquí lo defines como llave primaria
    )

    nombre_completo = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=True,
        null=True,
    )

    telefono = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{7,15}$',
                message='El número de celular debe contener entre 7 y 15 dígitos numéricos.'
            )
        ],
        blank=True,
        null=True
    )

    imagen_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True,
        default='perfiles/perfil_default.jpg'  # Ruta por defecto si no se sube una imagen
    )

    descripción = models.TextField(blank=True, null=True)

    edad = models.PositiveIntegerField(blank=True, null=True)

    # 🔹 Género del usuario
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decirlo'),
    ]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, null=True)

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
    )

    codigo_verificacion = models.CharField(max_length=6, blank=True, null=True)
    email_verificado = models.BooleanField(default=False)
    # Configuraciones para autenticación
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'telefono', 'nombre_completo']

    def __str__(self):
        return f"{self.username} - {self.email} - {self.telefono}"
    

class Message(models.Model):
    enviar = models.ForeignKey(Usuario, related_name='sent_messages', on_delete=models.CASCADE)
    recibir = models.ForeignKey(Usuario, related_name='received_messages', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(default=timezone.now)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha_envio']

    def _str_(self):
        return f'De {self.enviar} a {self.recibir}: {self.contenido[:20]}'
    


class Seguimiento(models.Model):
    seguidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='siguiendo_a',
        on_delete=models.CASCADE
    )
    seguido = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='seguidores_de',
        on_delete=models.CASCADE
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seguidor', 'seguido')
        ordering = ['-fecha_creacion']
        verbose_name = "Seguimiento"
        verbose_name_plural = "Seguimientos"

    def __str__(self):
        return f"{self.seguidor.username} sigue a {self.seguido.username}"
    
# -----------------------------------------------------------


class Publicacion(models.Model):
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='publicaciones')
    descripcion = models.TextField(blank=True, max_length=2200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    me_gusta = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='me_gusta', blank=True)

    def total_me_gusta(self):
        return self.me_gusta.count()

    class Meta:
        ordering = ['-fecha_creacion']



class ArchivoPublicacion(models.Model):
    publicacion = models.ForeignKey(Publicacion, related_name='archivos', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='publicaciones/')

    def es_imagen(self):
        return self.archivo.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))

    def es_video(self):
        return self.archivo.name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))

    def tipo(self):
        if self.es_imagen():
            return 'imagen'
        elif self.es_video():
            return 'video'
        return 'otro'


class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.autor.username}"
