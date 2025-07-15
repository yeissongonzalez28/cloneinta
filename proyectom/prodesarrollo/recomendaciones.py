# myapp/recomendaciones.py
from django.db.models import Count
from django.contrib.auth import get_user_model
from .models import Seguimiento

Usuario = get_user_model()

def obtener_usuarios_sugeridos(usuario_actual, limite=5):
    if not usuario_actual.is_authenticated:
        return Usuario.objects.none()

    ids_ya_seguidos = usuario_actual.siguiendo_a.values_list('seguido__username', flat=True)

    ids_excluidos = list(ids_ya_seguidos) + [usuario_actual.username]

    sugerencias = Usuario.objects.filter(
        seguidores_de__seguidor__in=ids_ya_seguidos
    ).exclude(
        username__in=ids_excluidos
    ).annotate(
        conteo_seguidores_mutuos=Count('seguidores_de__seguidor')
    ).order_by(
        '-conteo_seguidores_mutuos',
        '?'
    ).distinct()[:limite]

    if len(sugerencias) < limite:
        sugerencias_adicionales = Usuario.objects.exclude(
            username__in=ids_excluidos
        ).order_by('?')[:limite - len(sugerencias)]
        sugerencias = list(sugerencias) + list(sugerencias_adicionales)

    return sugerencias