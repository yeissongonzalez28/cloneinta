from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def timesince_con_y(value):
    tiempo = timesince(value)
    return tiempo.replace(",", " y ")
