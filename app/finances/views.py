import datetime
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expense, Category, Supplier
from .forms import ExpenseForm
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
