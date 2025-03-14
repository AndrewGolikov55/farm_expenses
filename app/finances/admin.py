# finances/admin.py

from django.contrib import admin
from .models import Expense, Category, Supplier

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'user', 'category', 'supplier', 'amount', 'date')
    list_filter = ('organization', 'category', 'supplier')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization')
    list_filter = ('organization',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization')
    list_filter = ('organization',)
