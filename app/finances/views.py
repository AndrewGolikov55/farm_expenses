import datetime
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expense, Category, Supplier
from .forms import ExpenseForm, CategoryForm, SupplierForm
from organizations.models import Membership
from django.db.models import Sum
from django.db.models.functions import TruncMonth


@login_required
def expenses_list_view(request):
    """Показываем все расходы текущей организации."""
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Вы не состоите ни в одной организации.")
        return redirect('org_list')  # no_organization.html

    org = membership.organization
    # Выбираем все расходы этой организации
    expenses = Expense.objects.filter(organization=org).order_by('-date')

    return render(request, 'finances/expenses_list.html', {
        'expenses': expenses,
        'org': org
    })


@login_required
def expense_create_view(request):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Вы не состоите ни в одной организации.")
        return redirect('org_list')
    org = membership.organization

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.organization = org
            expense.user = request.user
            expense.save()
            messages.success(request, "Расход добавлен.")
            return redirect('expenses_list')
    else:
        form = ExpenseForm()

    return render(request, 'finances/expense_create.html', {'form': form})


# Аналитика
@login_required
def analytics_index(request):
    """Аналитика финансов фермерского хозяйства."""
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Вы не состоите ни в одной организации.")
        return redirect('org_list')

    org = membership.organization

    # 1) Группируем расходы по месяцам (за последний год)
    one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
    data_by_month_qs = (
        Expense.objects
               .filter(organization=org, date__gte=one_year_ago)
               .annotate(month=TruncMonth('date'))
               .values('month')
               .annotate(total=Sum('amount'))
               .order_by('month')
    )
    # Превратим в списки для Chart.js
    month_labels = []
    month_values = []
    for row in data_by_month_qs:
        # row['month'] – это дата начала месяца (datetime)
        month_str = row['month'].strftime('%Y-%m')  # Пример: "2025-03"
        month_labels.append(month_str)
        month_values.append(float(row['total'] or 0))

    # 2) Распределение расходов по категориям
    data_by_cat_qs = (
        Expense.objects
               .filter(organization=org)
               .values('category__name')
               .annotate(total=Sum('amount'))
               .order_by('-total')
    )
    cat_labels = []
    cat_values = []
    for row in data_by_cat_qs:
        cat_name = row['category__name'] or "Без категории"
        cat_labels.append(cat_name)
        cat_values.append(float(row['total'] or 0))

    # 3) Общая сумма расходов (за всё время)
    total_expenses = (
        Expense.objects
               .filter(organization=org)
               .aggregate(sum_exp=Sum('amount'))
               .get('sum_exp') or 0
    )

    # Сериализуем списки в JSON
    context = {
        'org': org,
        'total_expenses': total_expenses,

        # Передаём сериализованные строки
        'month_labels_json': json.dumps(month_labels),
        'month_values_json': json.dumps(month_values),

        'cat_labels_json': json.dumps(cat_labels),
        'cat_values_json': json.dumps(cat_values),
    }
    return render(request, 'finances/analytics_index.html', context)


# Категории
@login_required
def categories_list_view(request):
    """Список категорий текущей организации."""
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Вы не состоите ни в одной организации.")
        return redirect('org_list')
    org = membership.organization

    categories = Category.objects.filter(organization=org).order_by('name')
    return render(request, 'finances/categories_list.html', {
        'categories': categories,
        'org': org,
    })


@login_required
def category_create_view(request):
    """Создание новой категории (например, доступно только админу)."""
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')
    if membership.role != 'admin':
        messages.error(request, "Только администратор может создавать категории.")
        return redirect('categories_list')

    org = membership.organization

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.organization = org
            cat.save()
            messages.success(request, "Категория создана.")
            return redirect('categories_list')
    else:
        form = CategoryForm()

    return render(request, 'finances/category_create.html', {
        'form': form,
        'org': org
    })


@login_required
def category_edit_view(request, cat_id):
    """Редактирование категории."""
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')
    if membership.role != 'admin':
        messages.error(request, "Только администратор может редактировать категории.")
        return redirect('categories_list')

    org = membership.organization
    category = get_object_or_404(Category, id=cat_id, organization=org)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория обновлена.")
            return redirect('categories_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'finances/category_edit.html', {
        'form': form,
        'org': org,
        'category': category,
    })


@login_required
def category_delete_view(request, cat_id):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership or membership.role != 'admin':
        messages.error(request, "Только администратор.")
        return redirect('categories_list')

    org = membership.organization
    category = get_object_or_404(Category, id=cat_id, organization=org)
    category.delete()
    messages.success(request, "Категория удалена.")
    return redirect('categories_list')


# Поставщики
@login_required
def suppliers_list_view(request):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Вы не состоите в организации.")
        return redirect('org_list')
    org = membership.organization

    suppliers = Supplier.objects.filter(organization=org).order_by('name')
    return render(request, 'finances/suppliers_list.html', {
        'suppliers': suppliers,
        'org': org,
    })


@login_required
def supplier_create_view(request):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')
    # Возможно, разрешим и member создавать
    # if membership.role != 'admin':
    #     messages.error(request, "Только администратор может создавать поставщиков.")
    #     return redirect('suppliers_list')

    org = membership.organization

    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            sup = form.save(commit=False)
            sup.organization = org
            sup.save()
            messages.success(request, "Поставщик создан.")
            return redirect('suppliers_list')
    else:
        form = SupplierForm()

    return render(request, 'finances/suppliers_create.html', {
        'form': form,
        'org': org
    })


@login_required
def supplier_edit_view(request, sup_id):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')

    org = membership.organization
    supplier = get_object_or_404(Supplier, id=sup_id, organization=org)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Поставщик обновлён.")
            return redirect('suppliers_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'finances/suppliers_edit.html', {
        'form': form,
        'org': org,
        'supplier': supplier,
    })


@login_required
def supplier_delete_view(request, sup_id):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')

    org = membership.organization
    supplier = get_object_or_404(Supplier, id=sup_id, organization=org)
    supplier.delete()
    messages.success(request, "Поставщик удалён.")
    return redirect('suppliers_list')