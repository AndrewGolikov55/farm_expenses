import datetime
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expense, Category, Supplier, IncomeCategory, Income
from .forms import ExpenseForm, CategoryForm, SupplierForm, IncomeForm, IncomeCategoryForm
from organizations.models import Membership
from django.db.models import Sum
from django.db.models.functions import TruncMonth


#@login_required
#def expenses_list_view(request):
#    """Показываем все расходы текущей организации + форму (пустую) для модального окна."""
#    membership = Membership.objects.filter(user=request.user).first()
#    if not membership:
#        messages.error(request, "Вы не состоите ни в одной организации.")
#        return redirect('org_list')
#
#    org = membership.organization
#    expenses = Expense.objects.filter(organization=org).order_by('-date')
#    membership = Membership.objects.filter(user=request.user).first()
#
#    # Пустая форма для всплывающего окна "Добавить расход"
#    form = ExpenseForm()
#
#    return render(request, 'finances/expenses_list.html', {
#        'expenses': expenses,
#        'org': org,
#        'form': form,
#        'membership': membership,
#    })


@login_required
def expense_create_view(request):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')

    if membership.role != 'admin':
        messages.error(request, "Только администратор может добавлять расходы.")
        return redirect('finances_index')

    org = membership.organization

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.organization = org
            expense.user = request.user
            expense.save()
            messages.success(request, "Расход добавлен.")
        else:
            messages.error(request, "Исправьте ошибки формы.")
    return redirect('finances_index')  # <-- на единую страницу "Финансы"


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


@login_required
def finances_balance_view(request):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')

    org = membership.organization

    total_expenses = Expense.objects.filter(organization=org).aggregate(models.Sum('amount'))['amount__sum'] or 0
    total_incomes = Income.objects.filter(organization=org).aggregate(models.Sum('amount'))['amount__sum'] or 0
    balance = total_incomes - total_expenses

    return render(request, 'finances/balance.html', {
        'org': org,
        'balance': balance,
        'total_expenses': total_expenses,
        'total_incomes': total_incomes,
    })


@login_required
def finances_index_view(request):
    """
    Единая страница "Финансы", где отображаются
    1) Список расходов
    2) Список доходов
    + модальные формы для добавления.
    """
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Вы не состоите ни в одной организации.")
        return redirect('org_list')

    org = membership.organization

    # Списки
    expenses = Expense.objects.filter(organization=org).order_by('-date')
    incomes = Income.objects.filter(organization=org).order_by('-date')

    # Пустые формы для модальных окон
    expense_form = ExpenseForm()
    income_form = IncomeForm()

    return render(request, 'finances/finances_index.html', {
        'org': org,
        'membership': membership,
        'expenses': expenses,
        'incomes': incomes,
        'expense_form': expense_form,
        'income_form': income_form
    })


# Категории
@login_required
def categories_list_view(request):
    """
    Одна страница со списком категорий расходов (Category) и доходов (IncomeCategory).
    Пустые формы для каждого типа, чтобы в модальных окнах создавать новые.
    """
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Вы не состоите ни в одной организации.")
        return redirect('org_list')

    org = membership.organization

    # Две выборки: расходные категории + доходные категории
    expense_cats = Category.objects.filter(organization=org).order_by('name')
    income_cats = IncomeCategory.objects.filter(organization=org).order_by('name')

    # Пустые формы для модальных окон
    expense_cat_form = CategoryForm()  
    income_cat_form = IncomeCategoryForm()

    return render(request, 'finances/categories_list.html', {
        'org': org,
        'membership': membership,

        'expense_cats': expense_cats,
        'income_cats': income_cats,

        'expense_cat_form': expense_cat_form,
        'income_cat_form': income_cat_form,
    })


@login_required
def expense_edit_view(request, exp_id):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership or membership.role != 'admin':
        messages.error(request, "Нет прав редактировать расходы.")
        return redirect('finances_index')

    org = membership.organization
    expense = get_object_or_404(Expense, id=exp_id, organization=org)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Расход обновлён.")
        else:
            messages.error(request, "Исправьте ошибки формы.")
        return redirect('finances_index')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'finances/expense_edit.html', {'form': form, 'org': org})


@login_required
def expense_delete_view(request, exp_id):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership or membership.role != 'admin':
        messages.error(request, "Нет прав для удаления расходов.")
        return redirect('finances_index')

    org = membership.organization
    expense = get_object_or_404(Expense, id=exp_id, organization=org)
    expense.delete()
    messages.success(request, "Расход удалён.")
    return redirect('finances_index')


@login_required
def category_create_view(request):
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
        else:
            messages.error(request, "Исправьте ошибки формы.")
        return redirect('categories_list')

    # Если GET — просто redirect
    return redirect('categories_list')


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

    form = SupplierForm()
    return render(request, 'finances/suppliers_list.html', {
        'suppliers': suppliers,
        'org': org,
        'form': form,
        'membership': membership,
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


#@login_required
#def incomes_list_view(request):
#    """Список доходов. Только видим, если состоим в организации."""
#    membership = Membership.objects.filter(user=request.user).first()
#    if not membership:
#        messages.error(request, "Вы не состоите ни в одной организации.")
#        return redirect('org_list')
#
#    org = membership.organization
#    incomes = Income.objects.filter(organization=org).order_by('-date')
#
#    # Пустая форма для модального окна "Добавить доход"
#    form = IncomeForm()
#
#    return render(request, 'finances/incomes_list.html', {
#        'incomes': incomes,
#        'org': org,
#        'form': form,
#        'membership': membership,
#    })


@login_required
def income_create_view(request):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')

    if membership.role != 'admin':
        messages.error(request, "Только администратор может добавлять доходы.")
        return redirect('finances_index')

    org = membership.organization

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.organization = org
            income.user = request.user
            income.save()
            messages.success(request, "Доход добавлен.")
        else:
            messages.error(request, "Исправьте ошибки формы.")
    return redirect('finances_index')


@login_required
def income_edit_view(request, inc_id):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership or membership.role != 'admin':
        messages.error(request, "Нет прав редактировать доходы.")
        return redirect('finances_index')

    org = membership.organization
    income = get_object_or_404(Income, id=inc_id, organization=org)

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, "Доход обновлён.")
        else:
            messages.error(request, "Исправьте ошибки формы.")
        return redirect('finances_index')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'finances/income_edit.html', {'form': form, 'org': org})


@login_required
def income_delete_view(request, inc_id):
    membership = Membership.objects.filter(user=request.user).first()
    if not membership or membership.role != 'admin':
        messages.error(request, "Нет прав для удаления доходов.")
        return redirect('finances_index')

    org = membership.organization
    income = get_object_or_404(Income, id=inc_id, organization=org)
    income.delete()
    messages.success(request, "Доход удалён.")
    return redirect('finances_index')


@login_required
def income_category_create_view(request):
    """Создание категории доходов (admin only)."""
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')
    if membership.role != 'admin':
        messages.error(request, "Только администратор может создавать категории доходов.")
        return redirect('categories_list')  # общий список категорий

    org = membership.organization

    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST)
        if form.is_valid():
            inc_cat = form.save(commit=False)
            inc_cat.organization = org
            inc_cat.save()
            messages.success(request, "Категория доходов создана.")
        else:
            messages.error(request, "Исправьте ошибки формы доходной категории.")
        return redirect('categories_list')

    return redirect('categories_list')


@login_required
def income_category_edit_view(request, icat_id):
    """Редактирование категории доходов."""
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Нет организации.")
        return redirect('org_list')
    if membership.role != 'admin':
        messages.error(request, "Только администратор может редактировать категории доходов.")
        return redirect('categories_list')

    org = membership.organization
    inc_cat = get_object_or_404(IncomeCategory, id=icat_id, organization=org)

    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST, instance=inc_cat)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория доходов обновлена.")
            return redirect('categories_list')
        else:
            messages.error(request, "Исправьте ошибки формы доходной категории.")
    else:
        form = IncomeCategoryForm(instance=inc_cat)

    return render(request, 'finances/income_category_edit.html', {
        'form': form,
        'org': org,
        'inc_cat': inc_cat,
    })


@login_required
def income_category_delete_view(request, icat_id):
    """Удаление категории доходов (admin only)."""
    membership = Membership.objects.filter(user=request.user).first()
    if not membership or membership.role != 'admin':
        messages.error(request, "Только администратор.")
        return redirect('categories_list')

    org = membership.organization
    inc_cat = get_object_or_404(IncomeCategory, id=icat_id, organization=org)
    inc_cat.delete()
    messages.success(request, "Категория доходов удалена.")
    return redirect('categories_list')
