from django.db import models
from decimal import Decimal
import uuid


class TripBudget(models.Model):
    """Overall budget summary for a trip."""
    trip = models.OneToOneField('trips.Trip', on_delete=models.CASCADE, related_name='budget')
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')

    class Meta:
        indexes = [
            models.Index(fields=['trip']),
        ]

    @property
    def total_spent(self):
        return self.expenses.aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    @property
    def remaining(self):
        return self.total_budget - self.total_spent

    def __str__(self):
        return f"Budget for {self.trip.name}: {self.currency} {self.total_budget}"


class Expense(models.Model):
    CATEGORY_TRANSPORT = 'transport'
    CATEGORY_STAY = 'stay'
    CATEGORY_FOOD = 'food'
    CATEGORY_ACTIVITIES = 'activities'
    CATEGORY_MISC = 'misc'

    CATEGORY_CHOICES = [
        (CATEGORY_TRANSPORT, 'Transport'),
        (CATEGORY_STAY, 'Stay'),
        (CATEGORY_FOOD, 'Food'),
        (CATEGORY_ACTIVITIES, 'Activities'),
        (CATEGORY_MISC, 'Miscellaneous'),
    ]

    budget = models.ForeignKey(TripBudget, on_delete=models.CASCADE, related_name='expenses')
    stop = models.ForeignKey('trips.Stop', on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_MISC)
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    qty_label = models.CharField(max_length=50, blank=True, default='', help_text='e.g. 3 nights, 2 tickets')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['date', 'category']
        indexes = [
            models.Index(fields=['budget', 'category']),
        ]

    def save(self, *args, **kwargs):
        # Auto-calculate amount from quantity * unit_cost if unit_cost > 0
        if self.unit_cost > 0 and self.quantity > 0:
            self.amount = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description}: {self.amount}"


class Invoice(models.Model):
    """Generated invoice for a trip's expenses."""
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
    ]

    budget = models.OneToOneField(TripBudget, on_delete=models.CASCADE, related_name='invoice')
    invoice_id = models.CharField(max_length=20, unique=True, editable=False)
    generated_date = models.DateField(auto_now_add=True)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    class Meta:
        indexes = [
            models.Index(fields=['invoice_id']),
        ]

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            short_uuid = uuid.uuid4().hex[:8].upper()
            self.invoice_id = f"INV-{short_uuid}"
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.budget.total_spent

    @property
    def tax_amount(self):
        return (Decimal(str(self.subtotal)) * self.tax_percent / Decimal('100')).quantize(Decimal('0.01'))

    @property
    def grand_total(self):
        return self.subtotal + self.tax_amount - self.discount

    def __str__(self):
        return f"{self.invoice_id} — {self.budget.trip.name}"
