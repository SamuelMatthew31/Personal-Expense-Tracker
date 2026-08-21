from django.urls import path
from .views import (
    RegisterView, dashboard,
    transaction_list, transaction_create,
    transaction_update, transaction_delete,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('transactions/', transaction_list, name='transaction_list'),
    path('transactions/add/', transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/edit/', transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', transaction_delete, name='transaction_delete'),
]