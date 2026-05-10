from django.contrib import admin
from .models import TripBudget, Expense


class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 1


@admin.register(TripBudget)
class TripBudgetAdmin(admin.ModelAdmin):
    list_display = ('trip', 'total_budget', 'currency')
    search_fields = ('trip__name',)
    inlines = [ExpenseInline]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'budget', 'category', 'amount', 'date')
    list_filter = ('category',)
