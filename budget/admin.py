from django.contrib import admin
from .models import TripBudget, Expense, Invoice


class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 1


class InvoiceInline(admin.StackedInline):
    model = Invoice
    extra = 0
    readonly_fields = ('invoice_id', 'generated_date')


@admin.register(TripBudget)
class TripBudgetAdmin(admin.ModelAdmin):
    list_display = ('trip', 'total_budget', 'currency')
    search_fields = ('trip__name',)
    inlines = [ExpenseInline, InvoiceInline]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'budget', 'category', 'quantity', 'unit_cost', 'amount', 'date')
    list_filter = ('category',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'budget', 'status', 'generated_date', 'tax_percent', 'discount')
    list_filter = ('status',)
    readonly_fields = ('invoice_id', 'generated_date')
