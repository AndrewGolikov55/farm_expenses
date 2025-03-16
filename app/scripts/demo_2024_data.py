"""
scripts/demo_2024_data.py

Запуск:
  python manage.py shell < scripts/demo_2024_data.py
"""

import random
import datetime
from django.contrib.auth.models import User
from organizations.models import Organization, Membership
from finances.models import Category, IncomeCategory, Supplier, Expense, Income

###########################
# 0) ИСХОДНЫЕ ПАРАМЕТРЫ
###########################
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpass"
USER_USERNAME = "user1"
USER_PASSWORD = "userpass"
ORG_NAME = "DemoFarm"
ORG_DESC = "Демонстрационная организация для 2024"

EXPENSE_CATEGORIES = [
    "Закупка семян",
    "Зарплата сотрудникам",
    "Коммунальные услуги",
    "Топливо для техники",
]

INCOME_CATEGORIES = [
    "Продажа продукции",
    "Субсидии от государства",
    "Аренда складов",
    "Прочие доходы",
]

SUPPLIERS = [
    ("Поставщик удобрений", "udobreniya@example.com"),
    ("Мясокомбинат", "meat@example.com"),
    ("Топливная компания", "fuel@example.com"),
    ("Поставщик техники", "tech@example.com"),
    ("Транспортная компания", "delivery@example.com"),
]

# Сколько операций (расходов и доходов) генерировать на месяц
MIN_PER_MONTH = 10
MAX_PER_MONTH = 20

# Диапазон сумм
EXPENSE_MIN = 1000
EXPENSE_MAX = 50000

INCOME_MIN = 10000
INCOME_MAX = 150000

###########################
# 1) СОЗДАЁМ/НАЙДЁМ ПОЛЬЗОВАТЕЛЕЙ
###########################
try:
    admin_user = User.objects.get(username=ADMIN_USERNAME)
    print(f"Пользователь {ADMIN_USERNAME} уже существует.")
except User.DoesNotExist:
    admin_user = User.objects.create_user(
        ADMIN_USERNAME, f"{ADMIN_USERNAME}@example.com", ADMIN_PASSWORD
    )
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    print(f"Создан суперпользователь: {ADMIN_USERNAME}/{ADMIN_PASSWORD}")

try:
    normal_user = User.objects.get(username=USER_USERNAME)
    print(f"Пользователь {USER_USERNAME} уже существует.")
except User.DoesNotExist:
    normal_user = User.objects.create_user(
        USER_USERNAME, f"{USER_USERNAME}@example.com", USER_PASSWORD
    )
    print(f"Создан пользователь: {USER_USERNAME}/{USER_PASSWORD}")

###########################
# 2) ОРГАНИЗАЦИЯ
###########################
org, created_org = Organization.objects.get_or_create(
    name=ORG_NAME,
    defaults={"description": ORG_DESC},
)
if created_org:
    print(f"Создана организация: {ORG_NAME}")
else:
    print(f"Организация {ORG_NAME} уже существует.")

# Membership
m1, _ = Membership.objects.get_or_create(
    user=admin_user, organization=org, defaults={"role": "admin"}
)
m2, _ = Membership.objects.get_or_create(
    user=normal_user, organization=org, defaults={"role": "member"}
)

###########################
# 3) КАТЕГОРИИ РАСХОДОВ/ДОХОДОВ
###########################
expense_categories_objs = []
for cat_name in EXPENSE_CATEGORIES:
    obj, _ = Category.objects.get_or_create(
        organization=org,
        name=cat_name,
        defaults={"description": f"Описание: {cat_name}"},
    )
    expense_categories_objs.append(obj)

income_categories_objs = []
for cat_name in INCOME_CATEGORIES:
    obj, _ = IncomeCategory.objects.get_or_create(
        organization=org,
        name=cat_name,
        defaults={"description": f"Описание: {cat_name}"},
    )
    income_categories_objs.append(obj)

###########################
# 4) ПОСТАВЩИКИ
###########################
supplier_objs = []
for sname, scontact in SUPPLIERS:
    obj, _ = Supplier.objects.get_or_create(
        organization=org,
        name=sname,
        defaults={"contact_info": scontact},
    )
    supplier_objs.append(obj)

###########################
# 5) ГЕНЕРАЦИЯ РАСХОДОВ/ДОХОДОВ
###########################
# Удалим возможные дубли:
# Expense.objects.filter(organization=org).delete()
# Income.objects.filter(organization=org).delete()

start_date = datetime.date(2025, 1, 1)
end_date = datetime.date(2025, 3, 20)

# Пройдём по месяцам 2024
current = start_date
while current <= end_date:
    year = current.year
    month = current.month

    # Сгенерируем random количество расходов/доходов
    expense_count = random.randint(MIN_PER_MONTH, MAX_PER_MONTH)
    income_count = random.randint(MIN_PER_MONTH, MAX_PER_MONTH)

    # Расходы
    for _ in range(expense_count):
        day = random.randint(1, 28)
        date_obj = datetime.date(year, month, day)

        Expense.objects.create(
            organization=org,
            user=random.choice([admin_user, normal_user]),
            category=random.choice(expense_categories_objs),
            supplier=random.choice(supplier_objs),
            description=f"Транзакция расхода на {date_obj}",
            amount=random.randint(EXPENSE_MIN, EXPENSE_MAX),
            date=date_obj
        )

    # Доходы
    for _ in range(income_count):
        day = random.randint(1, 28)
        date_obj = datetime.date(year, month, day)

        Income.objects.create(
            organization=org,
            user=random.choice([admin_user, normal_user]),
            category=random.choice(income_categories_objs),
            description=f"Транзакция дохода на {date_obj}",
            amount=random.randint(INCOME_MIN, INCOME_MAX),
            date=date_obj
        )

    # Следующий месяц
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1

    current = datetime.date(year, month, 1)

print("=== Данные за 2024 год успешно сгенерированы! ===")
