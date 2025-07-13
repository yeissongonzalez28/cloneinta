from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import RegistroForm
from .models import Usuario
from django.contrib.auth import login

# Create your views here.
def index(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')  # Usa el nombre de la url para inicio
        else:
            error = "Usuario o contraseña incorrectos."
    return render(request, 'inicio/index.html', {'error': error})


def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Encripta contraseña
            user.save()
            login(request, user)
            return redirect('index')  # Cambia 'home' por tu vista principal
    else:
        form = RegistroForm()
    return render(request, 'inicio/registro.html', {'form': form})


def inicio(request):
    return render(request, 'paginas/inicio.html')