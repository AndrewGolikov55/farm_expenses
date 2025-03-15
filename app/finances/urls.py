from django.urls import path
from . import views

urlpatterns = [
    # Единая страница "Финансы"
    path('', views.finances_index_view, name='finances_index'),

    path('expenses/create/', views.expense_create_view, name='expense_create'),
    path('expenses/<int:exp_id>/edit/', views.expense_edit_view, name='expense_edit'),
    path('expenses/<int:exp_id>/delete/', views.expense_delete_view, name='expense_delete'),

    # Analytic
    path('analytics_index/', views.analytics_index, name='analytics_index'),

    # Category
    path('categories/', views.categories_list_view, name='categories_list'),

    # Расходные категории (у вас уже есть)
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:cat_id>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<int:cat_id>/delete/', views.category_delete_view, name='category_delete'),

    # Доходные категории
    path('inc_categories/create/', views.income_category_create_view, name='income_category_create'),
    path('inc_categories/<int:icat_id>/edit/', views.income_category_edit_view, name='income_category_edit'),
    path('inc_categories/<int:icat_id>/delete/', views.income_category_delete_view, name='income_category_delete'),

    # Supplier
    path('suppliers/', views.suppliers_list_view, name='suppliers_list'),
    path('suppliers/create/', views.supplier_create_view, name='supplier_create'),
    path('suppliers/<int:sup_id>/edit/', views.supplier_edit_view, name='supplier_edit'),
    path('suppliers/<int:sup_id>/delete/', views.supplier_delete_view, name='supplier_delete'),

    # Incomes
    path('incomes/create/', views.income_create_view, name='income_create'),
    path('incomes/<int:inc_id>/edit/', views.income_edit_view, name='income_edit'),
    path('incomes/<int:inc_id>/delete/', views.income_delete_view, name='income_delete'),
]
