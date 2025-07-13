from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string

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
    )

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