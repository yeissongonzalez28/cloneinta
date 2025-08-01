from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def timesince_con_y(value):
    tiempo = timesince(value)
    return tiempo.replace(",", " y ")


@register.filter
def dict_key(value, key):
    """Permite acceder a un diccionario por clave en el template."""
    return value.get(key, "")
