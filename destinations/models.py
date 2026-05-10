from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    cost_index = models.DecimalField(max_digits=6, decimal_places=2)
    popularity_score = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-popularity_score', 'name']
        unique_together = ('name', 'country')
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['region']),
            models.Index(fields=['-popularity_score']),
        ]

    def __str__(self):
        return f"{self.name}, {self.country}"


class Activity(models.Model):
    CATEGORY_SIGHTSEEING = 'sightseeing'
    CATEGORY_FOOD = 'food'
    CATEGORY_ADVENTURE = 'adventure'
    CATEGORY_OTHER = 'other'

    CATEGORY_CHOICES = [
        (CATEGORY_SIGHTSEEING, 'Sightseeing'),
        (CATEGORY_FOOD, 'Food'),
        (CATEGORY_ADVENTURE, 'Adventure'),
        (CATEGORY_OTHER, 'Other'),
    ]

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_minutes = models.IntegerField(default=60)

    class Meta:
        ordering = ['city__name', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['estimated_cost']),
        ]

    def __str__(self):
        return f"{self.name} ({self.city.name})"
