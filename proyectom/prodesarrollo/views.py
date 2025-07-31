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
from django.db.models import Count


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
            'fecha': mensaje.fecha_envio.strftime('%H:%M'),
            'enviar': request.user.username  # Añadir el nombre del emisor
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
    Historia.limpiar_historias_expiradas()
    
    seguidos = Usuario.objects.filter(seguidores_de__seguidor=request.user)
    historias_activas = Historia.objects.filter(
        autor__in=[request.user] + list(seguidos),
        expiracion__gt=timezone.now()
    ).select_related('autor').order_by('autor', '-fecha_creacion')

    historias_por_autor = {}
    for historia in historias_activas:
        if historia.autor.username not in historias_por_autor:
            historias_por_autor[historia.autor.username] = historia

    form = PublicacionForm()
    publicaciones = Publicacion.objects.select_related('autor').all().order_by('-fecha_creacion')
    usuarios_sugeridos = obtener_usuarios_sugeridos(request.user, limite=5)


    usuarios_con_conteo_mutuo = []
    siguiendo_usernames = request.user.siguiendo_a.values_list('seguido__username', flat=True)
    for usuario_obj in usuarios_sugeridos:
        seguidores_mutuos_qs = Seguimiento.objects.filter(
            seguidor__username__in=siguiendo_usernames,
            seguido=usuario_obj
        ).select_related('seguidor')

        conteo_mutuo = seguidores_mutuos_qs.count()
        seguidor_mutuo = seguidores_mutuos_qs.first().seguidor if conteo_mutuo > 0 else None

        es_seguido_por_actual = Seguimiento.objects.filter(
            seguidor=request.user,
            seguido=usuario_obj
        ).exists()

        usuarios_con_conteo_mutuo.append({
            'usuario': usuario_obj,
            'conteo_seguidores_mutuos': conteo_mutuo,
            'seguidor_mutuo': seguidor_mutuo,
            'es_seguido_por_actual': es_seguido_por_actual,
        })


    contexto = {
        'form': form,
        'historia_form': HistoriaForm(),
        'usuarios_sugeridos': usuarios_con_conteo_mutuo,
        'publicaciones': publicaciones,
        'historias_activas': historias_por_autor.values()
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

def obtener_usuarios_sugeridos(usuario_actual, limite=20):
    siguiendo_usernames = list(
        Seguimiento.objects.filter(seguidor=usuario_actual)
        .values_list('seguido__username', flat=True)
    )

    sugerencias_usernames = Seguimiento.objects.filter(
        seguidor__username__in=siguiendo_usernames
    ).exclude(
        seguido__username__in= siguiendo_usernames + [usuario_actual.username]
    ).values('seguido__username').annotate(
        num_seguidores=Count('seguido__username')
    ).order_by('-num_seguidores').values_list('seguido__username', flat=True)

    sugeridos = Usuario.objects.filter(username__in=sugerencias_usernames)[:limite]

    return sugeridos
    


@login_required
def ver_todas_sugerencias(request):
    todas_sugerencias = obtener_usuarios_sugeridos(request.user, limite=20)
    usuarios_con_conteo_mutuo = []

    siguiendo_ids = request.user.siguiendo_a.values_list('seguido_id', flat=True)

    for sugerido in todas_sugerencias:
        seguidores_mutuos_qs = Seguimiento.objects.filter(
            seguidor_id__in=siguiendo_ids,
            seguido=sugerido
        ).select_related('seguidor')

        conteo_mutuo = seguidores_mutuos_qs.count()
        seguidor_mutuo = seguidores_mutuos_qs.first().seguidor if conteo_mutuo > 0 else None

        print("Sugerido:", sugerido.username)
        print("Seguidores mutuos:", [s.seguidor.username for s in seguidores_mutuos_qs])
        print("Seguidor mutuo seleccionado:", seguidor_mutuo.username if seguidor_mutuo else "Ninguno")

        es_seguido_por_actual = Seguimiento.objects.filter(
            seguidor=request.user,
            seguido=sugerido
        ).exists()

        usuarios_con_conteo_mutuo.append({
            'usuario': sugerido,
            'conteo_seguidores_mutuos': conteo_mutuo,
            'seguidor_mutuo': seguidor_mutuo,
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
        print("Archivos recibidos:", request.FILES)
        print("Formulario válido:", form.is_valid())
        print("Errores del formulario:", form.errors)

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
        archivos = request.FILES.getlist('archivos')

        extensiones_validas = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'mov', 'avi', 'mkv']
        for archivo in archivos:
            ext = archivo.name.split('.')[-1].lower()
            if ext not in extensiones_validas:
                form.add_error(None, f"El archivo '{archivo.name}' no es válido.")
            if archivo.size > 1024 * 1024 * 1024:
                form.add_error(None, f"El archivo '{archivo.name}' supera el límite de 1 GB.")

        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            publicacion.save()

            aspect_ratio = request.POST.get('aspect_ratio', '4:5')

            for archivo in archivos:
                ArchivoPublicacion.objects.create(
                    publicacion=publicacion,
                    archivo=archivo,
                    aspect_ratio=aspect_ratio
                )

            return redirect('inicio')

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

@login_required
def reels(request):
    return render(request,'paginas/reels.html')

# ---------------------------------reels------------------------------------

@login_required
def crear_reel(request):
    if request.method == 'POST':
        form = ReelForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.autor = request.user
            reel.save()
            return redirect('reels_feed')
    else:
        form = ReelForm()
    return render(request, 'CRUD/crear_reels.html', {'form': form})

from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

def reels_feed(request):
    page = int(request.GET.get('page', 1))
    qs = Reel.objects.select_related('autor').prefetch_related('likes')
    paginator = Paginator(qs, 5)  # 5 reels por “página”
    page_obj = paginator.get_page(page)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for r in page_obj:
            data.append({
                'id': r.pk,
                'video_url': r.video.url,
                'miniatura_url': r.miniatura.url if r.miniatura else '',
                'autor': str(r.autor),
                'autor_username': r.autor.username,
                'autor_imagen': r.autor.imagen_perfil.url if r.autor.imagen_perfil else '/static/img/perfil_default.png',  # 🔹 AQUI
                'titulo': r.titulo,
                'audio': r.audio_titulo or 'Audio original',
                'likes': r.likes.count(),
                'vistas': r.vistas,
                'ya_likeado': request.user in r.likes.all(),
            })
        return JsonResponse({'items': data, 'has_next': page_obj.has_next()})
    return render(request, 'paginas/reels.html', {'page_obj': page_obj})

@require_POST
@login_required
def toggle_like_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    if request.user in reel.likes.all():
        reel.likes.remove(request.user)
        likeado = False
    else:
        reel.likes.add(request.user)
        likeado = True
    return JsonResponse({'ok': True, 'likeado': likeado, 'likes': reel.likes.count()})

@require_POST
@login_required
def sumar_vista_reel(request, pk):
    reel = get_object_or_404(Reel, pk=pk)
    reel.vistas = models.F('vistas') + 1
    reel.save(update_fields=['vistas'])
    reel.refresh_from_db(fields=['vistas'])
    return JsonResponse({'ok': True, 'vistas': reel.vistas})
