from django.urls import path
from . import views

urlpatterns = [
    path('expenses/', views.expenses_list_view, name='expenses_list'),
    path('expenses/create/', views.expense_create_view, name='expense_create'),
    # Аналогично: categories_list, categories_create, suppliers_list, ...
    path('analytics_index/', views.analytics_index, name='analytics_index'),
]
