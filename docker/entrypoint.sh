#!/bin/sh

# Миграция БД
python manage.py makemigrations config users organizations finances
python manage.py migrate

# Проверка и создание суперпользователя
python create_admin.py

# Запуск основного процесса контейнера
python manage.py runserver 0.0.0.0:8000
#gunicorn mediassyst.wsgi:application --bind 0.0.0.0:8000