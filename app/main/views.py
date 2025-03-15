from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from finances.models import Expense, Category, Supplier, IncomeCategory, Income
from organizations.models import Membership


@login_required
def index(request):
    # 1) membership
    membership = Membership.objects.filter(user=request.user).select_related('organization').first()

    # 2) Подсчёт «быстрых фактов»
    if membership and membership.organization:
        org = membership.organization
        total_exp_count = Expense.objects.filter(organization=org).count()
        total_inc_count = Income.objects.filter(organization=org).count()
        total_suppliers = Supplier.objects.filter(organization=org).count()
        total_exp_cats = Category.objects.filter(organization=org).count()
        total_inc_cats = IncomeCategory.objects.filter(organization=org).count()

        # 3) Последние 5 операций (расходы + доходы)
        #    Объединим QuerySet: 
        from itertools import chain
        last_expenses = Expense.objects.filter(organization=org).order_by('-date')[:5]
        last_incomes = Income.objects.filter(organization=org).order_by('-date')[:5]

        # Превращаем в общую структуру
        # type='exp' или 'inc'
        # Сортировка: max date -> first
        from operator import attrgetter
        combined_ops = []

        for e in last_expenses:
            combined_ops.append({
                'type': 'exp',
                'amount': e.amount,
                'date': e.date,
                'description': e.description,
            })
        for i in last_incomes:
            combined_ops.append({
                'type': 'inc',
                'amount': i.amount,
                'date': i.date,
                'description': i.description,
            })

        # Сортируем по date (desc)
        combined_ops_sorted = sorted(combined_ops, key=lambda x: x['date'], reverse=True)
        last_operations = combined_ops_sorted[:5]

    else:
        org = None
        total_exp_count = 0
        total_inc_count = 0
        total_suppliers = 0
        total_exp_cats = 0
        total_inc_cats = 0
        last_operations = []

    context = {
        'membership': membership,
        'org': org,
        'total_exp_count': total_exp_count,
        'total_inc_count': total_inc_count,
        'total_suppliers': total_suppliers,
        'total_exp_cats': total_exp_cats,
        'total_inc_cats': total_inc_cats,
        'last_operations': last_operations,
    }
    return render(request, 'main/index.html', context)
