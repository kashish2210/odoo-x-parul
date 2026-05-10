from django.db import models


class TripBudget(models.Model):
    """Overall budget summary for a trip."""
    trip = models.OneToOneField('trips.Trip', on_delete=models.CASCADE, related_name='budget')
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')

    class Meta:
        indexes = [
            models.Index(fields=['trip']),
        ]

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
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['date', 'category']
        indexes = [
            models.Index(fields=['budget', 'category']),
        ]

    def __str__(self):
        return f"{self.description}: {self.amount}"
