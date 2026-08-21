from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import Transaction
from .forms import TransactionForm
from datetime import date
import calendar
from django.db.models.functions import TruncMonth

MONTH_NAMES_ID = {
    1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
    5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
    9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember',
}

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

    selected_type = request.GET.get('type', '')
    selected_category = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if selected_type:
        transactions = transactions.filter(type=selected_type)

    if selected_category:
        transactions = transactions.filter(category__icontains=selected_category)

    if date_from:
        transactions = transactions.filter(transaction_date__gte=date_from)

    if date_to:
        transactions = transactions.filter(transaction_date__lte=date_to)

    context = {
        'transactions': transactions,
        'selected_type': selected_type,
        'selected_category': selected_category,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'expenses/transaction_list.html', context)


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

@login_required
def monthly_report(request):
    transactions = Transaction.objects.filter(user=request.user)

    today = date.today()
    selected_year = int(request.GET.get('year', today.year))
    selected_month = int(request.GET.get('month', today.month))
    lang = request.GET.get('lang', 'id')

    month_transactions = transactions.filter(
        transaction_date__year=selected_year,
        transaction_date__month=selected_month
    )

    income = month_transactions.filter(type='IN').aggregate(total=Sum('amount'))['total'] or 0
    expense = month_transactions.filter(type='EX').aggregate(total=Sum('amount'))['total'] or 0
    balance = income - expense

    category_breakdown = (
        month_transactions.filter(type='EX')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    available_years = transactions.dates('transaction_date', 'year')
    available_years = sorted(set(d.year for d in available_years), reverse=True)
    if not available_years:
        available_years = [today.year]

    if lang == 'en':
        month_name = calendar.month_name[selected_month]
        months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    else:
        month_name = MONTH_NAMES_ID[selected_month]
        months = [(i, MONTH_NAMES_ID[i]) for i in range(1, 13)]

    context = {
        'income': income,
        'expense': expense,
        'balance': balance,
        'category_breakdown': category_breakdown,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'month_name': month_name,
        'available_years': available_years,
        'months': months,
        'month_transactions': month_transactions,
        'lang': lang,
    }
    return render(request, 'expenses/monthly_report.html', context)