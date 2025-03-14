from django.db import models
from django.conf import settings
from organizations.models import Organization

class Category(models.Model):
    """Категория расходов (семена, удобрения, зарплата и т.д.)."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Привязка к организации (по логике: категория видна только в своей ферме)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    """Поставщик товаров или услуг."""
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Expense(models.Model):
    """Расходы фермы."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.category} - {self.amount} ({self.date})"
