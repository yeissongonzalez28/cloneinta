from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import *
from .models import *
from django.contrib.auth import login
from django.contrib import messages
import random
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .recomendaciones import obtener_usuarios_sugeridos
from django.contrib.auth import get_user_model
Usuario = get_user_model()
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

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
from django.views.decorators.csrf import csrf_exempt

@login_required
def mensajes(request):
    usuario_actual = request.user  # Asumiendo que usas `Usuario` como modelo de usuario
    seguidos = Usuario.objects.filter(
        seguidores_de__seguidor=usuario_actual
    ).distinct()

    return render(request, 'paginas/mensajes.html', {
        'seguidos': seguidos,
    })


@login_required
def chat(request, username):
    receptor = get_object_or_404(Usuario, username=username)

    mensajes = Message.objects.filter(
        enviar__in=[request.user, receptor],
        recibir__in=[request.user, receptor]
    ).order_by('fecha_envio')

    return render(request, 'paginas/mensajes.html', {
        'receptor': receptor,
        'mensajes': mensajes
    })

@csrf_exempt
@login_required
def enviar_mensaje(request):
    if request.method == 'POST':
        contenido = request.POST.get('mensaje')
        receptor_username = request.POST.get('receptor')
        receptor = Usuario.objects.get(username=receptor_username)

        mensaje = Message.objects.create(
            enviar=request.user,
            recibir=receptor,
            contenido=contenido,
            fecha_envio=timezone.now()
        )

        return JsonResponse({
            'estado': 'ok',
            'mensaje': mensaje.contenido,
            'fecha': mensaje.fecha_envio.strftime('%H:%M')
        })
    return JsonResponse({'estado': 'error'})

def obtener_mensajes(request, username):
    receptor = get_object_or_404(Usuario, username=username)
    mensajes = Message.objects.filter(
        enviar__in=[request.user, receptor],
        recibir__in=[request.user, receptor]
    ).order_by('fecha_envio')

    data = [
        {
            'contenido': msg.contenido,
            'enviar': msg.enviar.username,
            'fecha': msg.fecha_envio.strftime('%H:%M')
        }
        for msg in mensajes
    ]

    return JsonResponse({'mensajes': data})

# ----------------------------------------
@login_required
def inicio(request):
    # Limpiar historias expiradas primero
    Historia.limpiar_historias_expiradas()
    
    # Obtener historias activas
    seguidos = Usuario.objects.filter(seguidores_de__seguidor=request.user)
    historias_activas = Historia.objects.filter(
        autor__in=[request.user] + list(seguidos),
        expiracion__gt=timezone.now()
    ).select_related('autor').order_by('autor', '-fecha_creacion')

    # Agrupar historias por autor y mantener solo la más reciente
    historias_por_autor = {}
    for historia in historias_activas:
        if historia.autor.username not in historias_por_autor:
            historias_por_autor[historia.autor.username] = historia

    form = PublicacionForm()
    publicaciones = Publicacion.objects.select_related('autor').all().order_by('-fecha_creacion')
    usuarios_sugeridos = obtener_usuarios_sugeridos(request.user, limite=5)

    usuarios_con_conteo_mutuo = []
    for usuario_obj in usuarios_sugeridos:
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
        'form': form,
        'historia_form': HistoriaForm(),
        'usuarios_sugeridos': usuarios_con_conteo_mutuo,
        'publicaciones': publicaciones,
        'historias_activas': historias_por_autor.values()  # Añadir historias al contexto
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

@login_required
def perfil(request, username):
    usuario = get_object_or_404(Usuario, username=username)

    publicacion_count = usuario.publicaciones.count()
    follower_count = Seguimiento.objects.filter(seguido=usuario).count()
    following_count = Seguimiento.objects.filter(seguidor=usuario).count()

    context = {
        'user': usuario,
        'publicaciones': publicacion_count,
        'follower_count': follower_count,
        'following_count': following_count,
    }
    return render(request, 'paginas/perfil.html', context)

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil', username=request.user.username)
    else:
        form = EditarPerfilForm(instance=request.user)

    return render(request, 'paginas/editar_perfil.html', {'form': form})

# ------------------------------------------------------
@login_required
def crear_publicacion(request):
    if request.method == 'POST':
        form = PublicacionForm(request.POST)
        archivos = request.FILES.getlist('archivos')  # 'archivos' debe coincidir con el name del input file

        # Validación manual
        extensiones_validas = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mkv']
        for archivo in archivos:
            ext = archivo.name.split('.')[-1].lower()
            if ext not in extensiones_validas:
                form.add_error(None, f"El archivo '{archivo.name}' no es una extensión válida.")
            if archivo.size > 1024 * 1024 * 1024:
                form.add_error(None, f"El archivo '{archivo.name}' supera el límite de 1 GB.")

        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            publicacion.save()

            for archivo in archivos:
                ArchivoPublicacion.objects.create(publicacion=publicacion, archivo=archivo)

            return redirect('inicio')  # Cambia esto según tu ruta

    else:
        form = PublicacionForm()

    publicaciones = Publicacion.objects.prefetch_related('archivos').all()

    return render(request, 'paginas/inicio.html', {'form': form, 'publicaciones': publicaciones})

def buscar_usuarios(request):
    query = request.GET.get('q', '')
    usuarios = []
    
    if query:
        usuarios = Usuario.objects.filter(
            username__icontains=query
        ).exclude(username=request.user.username)[:5]  # Limitamos a 5 resultados
        
        resultados = []
        for usuario in usuarios:
            resultados.append({
                'username': usuario.username,
                'nombre_completo': usuario.nombre_completo,
                'avatar': usuario.imagen_perfil.url if usuario.imagen_perfil else '/media/perfiles/perfil_default.jpg',
                'seguidores': usuario.seguidores_de.count()
            })
        
        return JsonResponse({'usuarios': resultados})
    
    return JsonResponse({'usuarios': []})

@login_required
@require_http_methods(["POST"])
def crear_historia(request):
    form = HistoriaForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            historia = form.save(commit=False)
            historia.autor = request.user
            historia.save()
            
            return JsonResponse({
                'status': 'success',
                'historia_id': historia.id,
                'url': historia.archivo.url
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)
    else:
        return JsonResponse({
            'status': 'error',
            'error': form.errors
        }, status=400)

@login_required
def obtener_historias(request):
    # Primero, limpiar historias expiradas
    Historia.limpiar_historias_expiradas()
    
    # Luego obtener solo historias activas
    seguidos = Usuario.objects.filter(seguidores_de__seguidor=request.user)
    historias_activas = Historia.objects.filter(
        autor__in=[request.user] + list(seguidos),
        expiracion__gt=timezone.now()
    ).select_related('autor')

    data = {}
    for historia in historias_activas:
        if historia.autor.username not in data:
            data[historia.autor.username] = {
                'username': historia.autor.username,
                'avatar': historia.autor.imagen_perfil.url if historia.autor.imagen_perfil else '/media/perfiles/perfil_default.jpg',
                'historias': []
            }
        data[historia.autor.username]['historias'].append({
            'id': historia.id,
            'url': historia.archivo.url,
            'tipo': 'video' if historia.es_video() else 'imagen',
            'fecha': historia.fecha_creacion.strftime('%H:%M'),
            'vista': request.user in historia.vistas.all()
        })

    return JsonResponse({'usuarios': list(data.values())})

@login_required
def obtener_historia(request, historia_id):
    try:
        historia = Historia.objects.select_related('autor').get(id=historia_id)
        
        # Marcar como vista
        if request.user != historia.autor:
            historia.vistas.add(request.user)
        
        return JsonResponse({
            'status': 'success',
            'historia': {
                'id': historia.id,
                'url': historia.archivo.url,
                'tipo': 'video' if historia.es_video() else 'imagen',
                'autor_username': historia.autor.username,
                'autor_avatar': historia.autor.imagen_perfil.url if historia.autor.imagen_perfil else '/media/perfiles/perfil_default.jpg',
                'timestamp': historia.fecha_creacion.strftime('%H:%M')
            }
        })
    except Historia.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Historia no encontrada'
        }, status=404)

@login_required
def obtener_historias_usuario(request, historia_id):
    try:
        historia = Historia.objects.select_related('autor').get(id=historia_id)
        historias_usuario = Historia.objects.filter(
            autor=historia.autor,
            expiracion__gt=timezone.now()
        ).order_by('fecha_creacion')
        
        historias_data = []
        for h in historias_usuario:
            # Marcar como vista si no es el autor
            if request.user != h.autor:
                h.vistas.add(request.user)
            
            historias_data.append({
                'id': h.id,
                'url': h.archivo.url,
                'tipo': 'video' if h.es_video() else 'imagen',
                'autor_username': h.autor.username,
                'autor_avatar': h.autor.imagen_perfil.url if h.autor.imagen_perfil else '/media/perfiles/perfil_default.jpg',
                'timestamp': h.fecha_creacion.strftime('%H:%M')
            })
        
        return JsonResponse({
            'status': 'success',
            'historias': historias_data
        })
    except Historia.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Historia no encontrada'
        }, status=404)

@login_required
def obtener_todas_historias(request):
    Historia.limpiar_historias_expiradas()
    
    # Obtener usuarios que sigue el usuario actual + el propio usuario
    seguidos = list(Usuario.objects.filter(
        seguidores_de__seguidor=request.user
    ).values_list('username', flat=True))
    seguidos.append(request.user.username)
    
    # Obtener todas las historias activas agrupadas por usuario
    historias = Historia.objects.filter(
        autor__username__in=seguidos,
        expiracion__gt=timezone.now()
    ).select_related('autor').order_by('autor', 'fecha_creacion')
    
    usuarios_historias = {}
    for historia in historias:
        if historia.autor.username not in usuarios_historias:
            usuarios_historias[historia.autor.username] = {
                'username': historia.autor.username,
                'avatar': historia.autor.imagen_perfil.url if historia.autor.imagen_perfil else '/media/perfiles/perfil_default.jpg',
                'historias': []
            }
        
        # Marcar historia como vista si corresponde
        if request.user != historia.autor:
            historia.vistas.add(request.user)
            
        usuarios_historias[historia.autor.username]['historias'].append({
            'id': historia.id,
            'url': historia.archivo.url,
            'tipo': 'video' if historia.es_video() else 'imagen',
            'timestamp': historia.fecha_creacion.strftime('%H:%M'),
            'vista': request.user in historia.vistas.all()
        })
    
    return JsonResponse({
        'status': 'success',
        'usuarios': list(usuarios_historias.values())
    })