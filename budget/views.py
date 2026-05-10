from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from trips.models import Trip
from .models import TripBudget, Expense, Invoice
from .forms import BudgetForm, ExpenseForm, InvoiceSettingsForm


@login_required
def billing_list_view(request):
    """List all trips with their billing/invoice status."""
    trips = Trip.objects.filter(user=request.user).prefetch_related('budget__invoice')
    query = request.GET.get('q', '')
    if query:
        trips = trips.filter(name__icontains=query)

    trip_data = []
    for trip in trips:
        budget = getattr(trip, 'budget', None)
        invoice = getattr(budget, 'invoice', None) if budget else None
        trip_data.append({
            'trip': trip,
            'budget': budget,
            'invoice': invoice,
            'total_spent': budget.total_spent if budget else 0,
            'status': invoice.get_status_display() if invoice else 'No Invoice',
        })

    return render(request, 'budget/billing_list.html', {
        'trip_data': trip_data,
        'query': query,
    })


@login_required
def invoice_view(request, trip_id):
    """Expense Invoice / Billing Screen (Screen 14 from wireframe)."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)

    # Get or create the budget
    budget, _ = TripBudget.objects.get_or_create(trip=trip, defaults={'total_budget': 0})

    # Get or create the invoice
    invoice, _ = Invoice.objects.get_or_create(budget=budget)

    expenses = budget.expenses.all().order_by('date', 'id')
    stops = trip.stops.select_related('city').all()

    return render(request, 'budget/invoice.html', {
        'trip': trip,
        'budget': budget,
        'invoice': invoice,
        'expenses': expenses,
        'stops': stops,
    })


@login_required
def set_budget_view(request, trip_id):
    """Set or update the budget for a trip."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    budget, _ = TripBudget.objects.get_or_create(trip=trip, defaults={'total_budget': 0})

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, f'Budget updated to {budget.currency} {budget.total_budget}')
            return redirect('budget:invoice', trip_id=trip.id)
    else:
        form = BudgetForm(instance=budget)

    return render(request, 'budget/set_budget.html', {
        'trip': trip,
        'form': form,
        'budget': budget,
    })


@login_required
def add_expense_view(request, trip_id):
    """Add an expense to a trip's budget."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    budget, _ = TripBudget.objects.get_or_create(trip=trip, defaults={'total_budget': 0})

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.budget = budget
            expense.save()
            messages.success(request, f'Expense "{expense.description}" added.')
            return redirect('budget:invoice', trip_id=trip.id)
    else:
        form = ExpenseForm()

    return render(request, 'budget/add_expense.html', {
        'trip': trip,
        'form': form,
    })


@login_required
def delete_expense_view(request, trip_id, expense_id):
    """Delete an expense."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    expense = get_object_or_404(Expense, id=expense_id, budget__trip=trip)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense removed.')
    return redirect('budget:invoice', trip_id=trip.id)


@login_required
def update_invoice_view(request, trip_id):
    """Update invoice settings (tax, discount, mark paid)."""
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    budget = get_object_or_404(TripBudget, trip=trip)
    invoice, _ = Invoice.objects.get_or_create(budget=budget)

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'mark_paid':
            invoice.status = Invoice.STATUS_PAID
            invoice.save(update_fields=['status'])
            messages.success(request, 'Invoice marked as Paid!')
        elif action == 'mark_pending':
            invoice.status = Invoice.STATUS_PENDING
            invoice.save(update_fields=['status'])
            messages.success(request, 'Invoice marked as Pending.')
        else:
            form = InvoiceSettingsForm(request.POST, instance=invoice)
            if form.is_valid():
                form.save()
                messages.success(request, 'Invoice settings updated.')

    return redirect('budget:invoice', trip_id=trip.id)
