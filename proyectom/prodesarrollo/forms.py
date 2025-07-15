from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from .models import Usuario
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

class RegistroForm(forms.ModelForm):
    email_or_phone = forms.CharField(
        label="Número de Celular o Correo Electrónico",
        widget=forms.TextInput(attrs={ 'placeholder': 'Número de celular o correo electrónico',
            'class': 'bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm text-white placeholder-neutral-400 focus:outline-none w-full'}),
        max_length=100
    )

    username = forms.CharField(
    label="Nombre de usuario",
    widget=forms.TextInput(attrs={
        'placeholder': 'Nombre de usuario',
        'class': 'bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm text-white placeholder-neutral-400 focus:outline-none w-full'
    })
    )

    nombre_completo = forms.CharField(
        label="Nombre completo",
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre completo',
            'class': 'bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm text-white placeholder-neutral-400 focus:outline-none w-full'
        })
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm text-white placeholder-neutral-400 focus:outline-none w-full'
        })
    )

    password_confirm = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmar contraseña',
            'class': 'bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm text-white placeholder-neutral-400 focus:outline-none w-full'
        })
    )
    class Meta:
        model = Usuario
        fields = ['username', 'nombre_completo', 'email_or_phone', 'password']

    def clean_username(self):
        username = self.cleaned_data['username']
        # Estas dos líneas deben estar indentadas con 4 espacios (o 1 tabulación)
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya existe.")
        return username
    
    def clean_email_or_phone(self):
        value = self.cleaned_data['email_or_phone']

        try:
            validate_email(value)
            self.cleaned_data['email'] = value
            return value
        except ValidationError:
            pass  # No es un correo

        if re.fullmatch(r'^\+?\d{7,15}$', value):
            self.cleaned_data['telefono'] = value
            return value

        raise ValidationError("Ingresa un correo electrónico válido o un número de teléfono válido.")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        user.email = self.cleaned_data.get('email', None)
        user.telefono = self.cleaned_data.get('telefono', None)

        necesita_verificacion = False

        if user.email:
            # Requiere verificación por correo
            codigo = get_random_string(length=6, allowed_chars='1234567890')
            user.codigo_verificacion = codigo
            user.email_verificado = False
            necesita_verificacion = True

            send_mail(
                'Código de verificación',
                f'Tu código de verificación es: {codigo}',
                'noreply@tuapp.com',
                [user.email],
                fail_silently=False,
            )
        else:
            user.email_verificado = True
            user.codigo_verificacion = None

        if commit:
            user.save()
        return user, necesita_verificacion


class LoginForm(forms.Form):
    identificador = forms.CharField(
        label="Correo, teléfono o usuario",
        widget=forms.TextInput(attrs={'placeholder': 'Correo, teléfono o usuario',
            'class': 'bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm text-white placeholder-neutral-400 focus:outline-none w-full'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña',
            'class': 'bg-neutral-900 border border-neutral-700 rounded px-3 py-2 text-sm text-white placeholder-neutral-400 focus:outline-none w-full'})
    )