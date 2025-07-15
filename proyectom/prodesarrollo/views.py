from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import RegistroForm
from .forms import LoginForm
from .models import *
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
        form = RegistroForm(request.POST)
        if form.is_valid():
            user, necesita_verificacion = form.save()
            if necesita_verificacion:
                # Redirige a la vista de verificación (correo)
                return redirect('verificacion')  # Usa el nombre correcto de tu URL
            else:
                # Redirige directo al login si se registró con teléfono
                return redirect('index')  # Usa el nombre correcto de tu URL
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


@login_required
def mensajes(request):
    return render(request, 'paginas/mensajes.html')

@login_required
def chat(request, username):
    receiver = get_object_or_404(Usuario, username=username)
    return render(request, 'paginas/mensajes.html', {
        'receiver': receiver
    })


from .recomendaciones import obtener_usuarios_sugeridos
from django.contrib.auth import get_user_model
Usuario = get_user_model()

@login_required
def inicio(request):
    usuarios_sugeridos = obtener_usuarios_sugeridos(request.user, limite=5)

    usuarios_con_conteo_mutuo = []
    for usuario_obj in usuarios_sugeridos:
        conteo_mutuo = Seguimiento.objects.filter(
            seguidor__in=request.user.siguiendo_a.values_list('seguido__username', flat=True),
            seguido=usuario_obj
        ).count()

        # NUEVA LÓGICA EN LA VISTA: Verificar si el usuario actual ya sigue a este sugerido
        # Esto se hace aquí, antes de pasar los datos a la plantilla.
        es_seguido_por_actual = Seguimiento.objects.filter(
            seguidor=request.user,
            seguido=usuario_obj
        ).exists() # .exists() devuelve True o False

        usuarios_con_conteo_mutuo.append({
            'usuario': usuario_obj,
            'conteo_seguidores_mutuos': conteo_mutuo,
            'es_seguido_por_actual': es_seguido_por_actual, # Añadimos esta bandera booleana al diccionario
        })

    contexto = {
        'usuarios_sugeridos': usuarios_con_conteo_mutuo,
    }
    return render(request, 'paginas/inicio.html', contexto)


@login_required
def seguir_usuario(request, nombre_usuario):
    usuario_a_seguir = get_object_or_404(Usuario, username=nombre_usuario)

    if request.user == usuario_a_seguir:
        messages.error(request, "¡No puedes seguirte a ti mismo!")
        return redirect('inicio')

    instancia_seguimiento = Seguimiento.objects.filter(
        seguidor=request.user,
        seguido=usuario_a_seguir
    ).first()

    if instancia_seguimiento:
        instancia_seguimiento.delete()
        messages.success(request, f"Dejaste de seguir a @{nombre_usuario}.")
    else:
        Seguimiento.objects.create(
            seguidor=request.user,
            seguido=usuario_a_seguir
        )
        messages.success(request, f"Ahora sigues a @{nombre_usuario}.")

    return redirect(request.META.get('HTTP_REFERER', 'inicio'))


@login_required
def ver_todas_sugerencias(request):
    todas_sugerencias = obtener_usuarios_sugeridos(request.user, limite=20)
    usuarios_con_conteo_mutuo = []
    for usuario_obj in todas_sugerencias:
        conteo_mutuo = Seguimiento.objects.filter(
            seguidor__in=request.user.siguiendo_a.values_list('seguido__username', flat=True),
            seguido=usuario_obj
        ).count()

        es_seguido_por_actual = Seguimiento.objects.filter(
            seguidor=request.user,
            seguido=usuario_obj
        ).exists()

        usuarios_con_conteo_mutuo.append({
            'usuario': usuario_obj,
            'conteo_seguidores_mutuos': conteo_mutuo,
            'es_seguido_por_actual': es_seguido_por_actual,
        })
    contexto = {
        'usuarios_sugeridos': usuarios_con_conteo_mutuo,
        'mostrar_titulo_todos': True
    }
    return render(request, 'myapp/pagina_todas_sugerencias.html', contexto)


# ---------------------------


def perfil(request, username):
    usuario = get_object_or_404(Usuario, username=username)


    follower_count = Seguimiento.objects.filter(seguido=usuario).count()
    following_count = Seguimiento.objects.filter(seguidor=usuario).count()

    context = {
        'user': usuario,

        'follower_count': follower_count,
        'following_count': following_count,
    }
    return render(request, 'paginas/perfil.html', context)

def editar_perfil(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil', username=request.user.username)
    else:
        form = RegistroForm(instance=request.user)

    return render(request, 'paginas/editar_perfil.html', {'form': form})