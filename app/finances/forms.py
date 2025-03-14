from django import forms
from .models import Expense, Category, Supplier

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'supplier', 'amount', 'description', 'date']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_info']