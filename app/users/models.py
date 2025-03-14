from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('farmer', 'Фермер'),
        ('admin', 'Администратор хозяйства'),
        ('superadmin', 'Системный администратор'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='farmer')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
