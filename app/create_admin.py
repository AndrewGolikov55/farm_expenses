import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User   # noqa: E402

username = os.environ.get('DJANGO_ADMIN', 'admin')
password = os.environ.get('DJANGO_PASSWORD', 'admin')
email = os.environ.get('DJANGO_EMAIL', '')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Суперпользователь {username} создан.")
else:
    print(f"Суперпользователь {username} уже существует.")
