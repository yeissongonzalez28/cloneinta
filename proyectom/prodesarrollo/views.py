from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import RegistroForm
from .forms import LoginForm
from .models import Usuario
from django.contrib.auth import login
from django.contrib import messages
import random
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

# Create your views here.
def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identificador = form.cleaned_data['identificador']
            password = form.cleaned_data['password']

            # Buscar al usuario por username, correo o teléfono
            try:
                usuario = Usuario.objects.get(
                    username=identificador
                )
            except Usuario.DoesNotExist:
                try:
                    usuario = Usuario.objects.get(
                        email=identificador
                    )
                except Usuario.DoesNotExist:
                    try:
                        usuario = Usuario.objects.get(
                            telefono=identificador
                        )
                    except Usuario.DoesNotExist:
                        usuario = None

            if usuario is not None and usuario.check_password(password):
                login(request, usuario)
                return redirect('inicio')  # Cambia por tu vista principal
            else:
                messages.error(request, "El Campo es incorrecto o contraseña incorrecta.")
    else:
        form = LoginForm()

    return render(request, 'inicio/index.html', {'form': form})


def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Encripta contraseña
            user.save()
            login(request, user)
            return redirect('verificar')  # Cambia 'home' por tu vista principal
    else:
        form = RegistroForm()
    return render(request, 'inicio/registro.html', {'form': form})

def verificar_codigo(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        usuario = request.user
        if usuario.codigo_verificacion == codigo:
            usuario.email_verificado = True
            usuario.codigo_verificacion = ''
            usuario.save()
            return redirect('index')  # O donde quieras redirigir
        else:
            messages.error(request, 'Código incorrecto.')
    return render(request, 'inicio/verificacion.html')

@login_required
def reenviar_codigo(request):
    usuario = request.user

    if usuario.email:
        # Generar nuevo código
        nuevo_codigo = get_random_string(length=6, allowed_chars='1234567890')
        usuario.codigo_verificacion = nuevo_codigo
        usuario.email_verificado = False  # Asegúrate de reiniciar el estado
        usuario.save()

        # Enviar el nuevo código
        send_mail(
            'Nuevo código de verificación',
            f'Tu nuevo código de verificación es: {nuevo_codigo}',
            'noreply@tuapp.com',
            [usuario.email],
            fail_silently=False,
        )

        messages.success(request, 'Se ha enviado un nuevo código a tu correo.')
    else:
        messages.error(request, 'No se encontró un correo válido para reenviar el código.')

    return redirect('verificar')  # Asegúrate de tener esta vista en tu urls.py


# ----------------------------------------------------------------

def inicio(request):
    return render(request, 'paginas/inicio.html')