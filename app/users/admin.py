from django.contrib import admin
from .models import UserProfile  # пример, если такая модель есть

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role')
