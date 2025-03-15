import datetime
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expense, Category, Supplier, IncomeCategory, Income
from .forms import ExpenseForm, CategoryForm, SupplierForm, IncomeForm, IncomeCategoryForm
from organizations.models import Membership
from django.db.models import Sum
from django.db.models.functions import TruncMonth, ExtractYear, ExtractMonth


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
    membership = Membership.objects.filter(user=request.user).first()
    if not membership:
        messages.error(request, "Вы не состоите ни в одной организации.")
        return redirect('org_list')

    org = membership.organization

    # =========================
    # 1) Месячные расходы/доходы (за год) + Баланс
    # =========================
    one_year_ago = datetime.date.today() - datetime.timedelta(days=365)

    # Расходы по месяцам
    expense_by_month = (
        Expense.objects
               .filter(organization=org, date__gte=one_year_ago)
               .annotate(month=TruncMonth('date'))
               .values('month')
               .annotate(sum_exp=Sum('amount'))
               .order_by('month')
    )
    # Доходы по месяцам
    income_by_month = (
        Income.objects
              .filter(organization=org, date__gte=one_year_ago)
              .annotate(month=TruncMonth('date'))
              .values('month')
              .annotate(sum_inc=Sum('amount'))
              .order_by('month')
    )

    # Превращаем в словари: {month -> sum_exp}, {month -> sum_inc}
    expense_map = { row['month']: float(row['sum_exp'] or 0) for row in expense_by_month }
    income_map = { row['month']: float(row['sum_inc'] or 0) for row in income_by_month }

    # Собираем общий список месяцев
    all_months = sorted(set(expense_map.keys()) | set(income_map.keys()))
    month_labels = []
    expenses_list = []
    incomes_list = []
    balance_list = []

    for m in all_months:
        label_str = m.strftime('%Y-%m')
        month_labels.append(label_str)
        e_val = expense_map.get(m, 0)
        i_val = income_map.get(m, 0)
        expenses_list.append(e_val)
        incomes_list.append(i_val)
        balance_list.append(i_val - e_val)

    # Итоговые суммы
    total_expenses = sum(expenses_list)
    total_incomes = sum(incomes_list)
    balance = total_incomes - total_expenses

    # =========================
    # 2) Распределение расходов по категориям
    # =========================
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

    # =========================
    # 3) ТОП-5 доходных категорий
    # =========================
    top_income_cats = (
        Income.objects
              .filter(organization=org)
              .values('category__name')
              .annotate(sum_inc=Sum('amount'))
              .order_by('-sum_inc')[:5]
    )
    # Превратим в простой список словарей:
    top_incomes_list = []
    for row in top_income_cats:
        cname = row['category__name'] or "Без категории"
        top_incomes_list.append({
            'category': cname,
            'sum_inc': float(row['sum_inc'] or 0)
        })

    # =========================
    # 4) ТОП-5 поставщиков (по расходам)
    # =========================
    top_suppliers_qs = (
        Expense.objects
               .filter(organization=org)
               .values('supplier__name')
               .annotate(sum_exp=Sum('amount'))
               .order_by('-sum_exp')[:5]
    )
    top_suppliers_list = []
    for row in top_suppliers_qs:
        sname = row['supplier__name'] or "Без поставщика"
        top_suppliers_list.append({
            'supplier': sname,
            'sum_exp': float(row['sum_exp'] or 0)
        })

    # =========================
    # 5) Процент изменения расходов/доходов (текущий месяц vs предыдущий)
    # =========================
    today = datetime.date.today()
    # Текущий месяц
    current_month_exp = Expense.objects.filter(
        organization=org,
        date__year=today.year,
        date__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    current_month_inc = Income.objects.filter(
        organization=org,
        date__year=today.year,
        date__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Предыдущий месяц
    # (Упрощённо: если month=1 => previous => month=12, year -=1)
    prev_year = today.year
    prev_month = today.month - 1
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    prev_month_exp = Expense.objects.filter(
        organization=org,
        date__year=prev_year,
        date__month=prev_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    prev_month_inc = Income.objects.filter(
        organization=org,
        date__year=prev_year,
        date__month=prev_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    # Считаем процент изменения = ((cur - prev) / prev) * 100
    def pct_change(cur, prev):
        if prev == 0:
            return None
        return round((cur - prev) / prev * 100, 2)

    exp_change_pct = pct_change(current_month_exp, prev_month_exp)
    inc_change_pct = pct_change(current_month_inc, prev_month_inc)

    # =========================
    # 6) Простейший прогноз (скользящее среднее) на следующий месяц
    # =========================
    # Например, берём последние 3 месяца
    # (В реальной практике лучше ARIMA, Prophet, etc.)
    def simple_moving_average(values, window=3):
        """Берём последние `window` значений, если их мало - fallback."""
        if len(values) < window:
            return sum(values) / max(len(values), 1)
        return sum(values[-window:]) / window

    # expenses_list/incomes_list уже упорядочены по all_months
    # Предположим, expenses_list[-1] - это последняя сумма (текущий месяц).
    # Скользящее среднее - forecastExp, forecastInc
    forecast_exp = simple_moving_average(expenses_list)  # avg 3
    forecast_inc = simple_moving_average(incomes_list)

    # Округлим
    forecast_exp = round(forecast_exp, 2)
    forecast_inc = round(forecast_inc, 2)

    # =========================
    # Передаём в контекст
    # =========================
    context = {
        'org': org,
        'total_expenses': total_expenses,
        'total_incomes': total_incomes,
        'balance': balance,

        # Месячные графики
        'month_labels_json': json.dumps([m for m in month_labels]),
        'expenses_list_json': json.dumps(expenses_list),
        'incomes_list_json': json.dumps(incomes_list),
        'balance_list_json': json.dumps(balance_list),

        # Расходы по категориям (pie)
        'cat_labels_json': json.dumps(cat_labels),
        'cat_values_json': json.dumps(cat_values),

        # ТОП-5 доходных категорий
        'top_incomes_list': top_incomes_list,
        # ТОП-5 поставщиков
        'top_suppliers_list': top_suppliers_list,

        # Процент изменений
        'exp_change_pct': exp_change_pct,
        'inc_change_pct': inc_change_pct,

        # Прогноз (simple moving avg)
        'forecast_exp': forecast_exp,
        'forecast_inc': forecast_inc,
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
