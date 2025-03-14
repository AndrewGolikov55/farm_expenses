from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import RegistrationForm
from django.contrib import messages

def register_user(request):
    """Регистрация"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Если это UserCreationForm:
            user = form.save()  # Создаёт пользователя, пароль уже захэширован
            login(request, user)  # Авторизовать сразу (по желанию)
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect('index')
        else:
            messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def login_user(request):
    """Авторизация"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # если логин успешен — редирект на главную
            return redirect('index')
        else:
            messages.error(request, "Неверное имя пользователя или пароль!")
    return render(request, 'users/login.html')


def logout_user(request):
    """Выход из системы"""
    logout(request)
    return redirect('login')  # Возвращаем на страницу входа
