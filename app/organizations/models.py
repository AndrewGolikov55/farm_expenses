from django.db import models
from django.contrib.auth.models import User
import uuid

class Organization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Кто создал организацию (опционально)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_orgs')

    def __str__(self):
        return self.name

class Membership(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('member', 'Участник'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

    # Можно добавить unique_together
    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user.username} в {self.organization.name} ({self.role})"

class Invitation(models.Model):
    """Приглашение пользователя в организацию."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    email = models.EmailField()         # или username, если логин по имени
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    # Можно хранить статус: 'pending', 'accepted', 'declined' и т.п.

    def __str__(self):
        return f"Приглашение {self.email} в {self.organization.name}"
