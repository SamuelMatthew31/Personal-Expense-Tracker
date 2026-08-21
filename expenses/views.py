from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import Transaction
from .forms import TransactionForm


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)

    income = transactions.filter(type='IN').aggregate(total=Sum('amount'))['total'] or 0
    expense = transactions.filter(type='EX').aggregate(total=Sum('amount'))['total'] or 0
    balance = income - expense

    recent_transactions = transactions[:5]

    context = {
        'balance': balance,
        'income': income,
        'expense': expense,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'expenses/dashboard.html', context)

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'expenses/transaction_list.html', {'transactions': transactions})


@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaksi berhasil ditambahkan.')
            return redirect('transaction_list')
    else:
        form = TransactionForm()

    return render(request, 'expenses/transaction_form.html', {
        'form': form,
        'title': 'Tambah Transaksi',
    })


@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaksi berhasil diperbarui.')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)

    return render(request, 'expenses/transaction_form.html', {
        'form': form,
        'title': 'Edit Transaksi',
    })


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaksi berhasil dihapus.')
        return redirect('transaction_list')

    return render(request, 'expenses/transaction_confirm_delete.html', {'transaction': transaction})