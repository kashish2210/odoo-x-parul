from django.db import models


class PackingItem(models.Model):
    CATEGORY_CLOTHING = 'clothing'
    CATEGORY_DOCUMENTS = 'documents'
    CATEGORY_ELECTRONICS = 'electronics'
    CATEGORY_OTHER = 'other'

    CATEGORY_CHOICES = [
        (CATEGORY_CLOTHING, 'Clothing'),
        (CATEGORY_DOCUMENTS, 'Documents'),
        (CATEGORY_ELECTRONICS, 'Electronics'),
        (CATEGORY_OTHER, 'Other'),
    ]

    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, related_name='packing_items')
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    is_packed = models.BooleanField(default=False)

    class Meta:
        ordering = ['is_packed', 'category', 'name']
        indexes = [
            models.Index(fields=['trip', 'is_packed']),
        ]

    def __str__(self):
        return f"{self.name} ({self.trip.name})"


class TripNote(models.Model):
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, related_name='notes')
    stop = models.ForeignKey('trips.Stop', on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trip', '-created_at']),
        ]

    def __str__(self):
        return f"Note for {self.trip.name}"
