from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'inicio/index.html')

def registro(request):
    return render(request, 'inicio/registro.html')

def inicio(request):
    return render(request, 'paginas/inicio.html')