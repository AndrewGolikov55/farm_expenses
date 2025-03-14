from django.urls import path
from . import views

urlpatterns = [
    path('expenses/', views.expenses_list_view, name='expenses_list'),
    path('expenses/create/', views.expense_create_view, name='expense_create'),
    # Analytic
    path('analytics_index/', views.analytics_index, name='analytics_index'),

    # Category
    path('categories/', views.categories_list_view, name='categories_list'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:cat_id>/edit/', views.category_edit_view, name='category_edit'),
    path('categories/<int:cat_id>/delete/', views.category_delete_view, name='category_delete'),

    # Supplier
    path('suppliers/', views.suppliers_list_view, name='suppliers_list'),
    path('suppliers/create/', views.supplier_create_view, name='supplier_create'),
    path('suppliers/<int:sup_id>/edit/', views.supplier_edit_view, name='supplier_edit'),
    path('suppliers/<int:sup_id>/delete/', views.supplier_delete_view, name='supplier_delete'),
]
