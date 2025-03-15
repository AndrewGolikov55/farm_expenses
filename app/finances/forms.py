from django import forms
from .models import Expense, Category, Supplier, IncomeCategory, Income

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'supplier', 'amount', 'description', 'date']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category'
            }),
            'supplier': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_supplier'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Сумма',
                'id': 'id_amount'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание',
                'id': 'id_description',
                'style': 'height: 100px;'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_date'
            }),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название категории',
                'id': 'id_name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание',
                'id': 'id_description',
                'style': 'height: 80px;'
            })
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_info']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название поставщика',
                'id': 'id_name'
            }),
            'contact_info': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Контактная информация',
                'id': 'id_contact_info',
                'style': 'height: 80px;'
            })
        }


class IncomeCategoryForm(forms.ModelForm):
    class Meta:
        model = IncomeCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название категории доходов',
                'id': 'id_income_cat_name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание доходной категории',
                'id': 'id_income_cat_description',
                'style': 'height: 80px;'
            })
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['category', 'amount', 'description', 'date']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Сумма дохода',
                'id': 'id_amount'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание',
                'id': 'id_description',
                'style': 'height: 100px;'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_date'
            }),
        }
