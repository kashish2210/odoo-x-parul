from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    path('', views.billing_list_view, name='billing_list'),
    path('<int:trip_id>/', views.invoice_view, name='invoice'),
    path('<int:trip_id>/set-budget/', views.set_budget_view, name='set_budget'),
    path('<int:trip_id>/add-expense/', views.add_expense_view, name='add_expense'),
    path('<int:trip_id>/expense/<int:expense_id>/delete/', views.delete_expense_view, name='delete_expense'),
    path('<int:trip_id>/update-invoice/', views.update_invoice_view, name='update_invoice'),
]
