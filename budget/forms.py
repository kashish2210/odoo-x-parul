from django import forms
from .models import TripBudget, Expense, Invoice


class BudgetForm(forms.ModelForm):
    """Form for setting the trip budget."""
    class Meta:
        model = TripBudget
        fields = ['total_budget', 'currency']
        widgets = {
            'total_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 50000',
                'step': '0.01',
            }),
            'currency': forms.Select(attrs={
                'class': 'form-control',
            }, choices=[
                ('INR', 'INR (₹)'),
                ('USD', 'USD ($)'),
                ('EUR', 'EUR (€)'),
                ('GBP', 'GBP (£)'),
                ('JPY', 'JPY (¥)'),
            ]),
        }


class ExpenseForm(forms.ModelForm):
    """Form for adding an expense."""
    class Meta:
        model = Expense
        fields = ['category', 'description', 'qty_label', 'unit_cost', 'amount']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Hotel booking Paris',
            }),
            'qty_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 3 nights, 2 tickets',
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total amount',
                'step': '0.01',
            }),
        }


class InvoiceSettingsForm(forms.ModelForm):
    """Form for editing invoice tax & discount."""
    class Meta:
        model = Invoice
        fields = ['tax_percent', 'discount']
        widgets = {
            'tax_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5.00',
                'step': '0.01',
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
        }
