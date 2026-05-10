from django.conf import settings
from django.db import models


class Trip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trips')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    cover_photo = models.ImageField(upload_to='trips/covers/', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_public = models.BooleanField(default=False)
    accommodation_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-start_date', '-id']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_public']),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Stop(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='stops')
    city = models.ForeignKey('destinations.City', on_delete=models.PROTECT, related_name='trip_stops')
    arrival_date = models.DateField()
    departure_date = models.DateField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'arrival_date', 'id']
        constraints = [
            models.UniqueConstraint(fields=['trip', 'order'], name='unique_stop_order_per_trip'),
        ]
        indexes = [
            models.Index(fields=['trip', 'order']),
        ]

    def __str__(self):
        return f"{self.trip.name} - {self.city.name} (#{self.order})"


class StopActivity(models.Model):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='stop_activities')
    activity = models.ForeignKey('destinations.Activity', on_delete=models.PROTECT, related_name='scheduled_stops')
    scheduled_time = models.TimeField(blank=True, null=True)

    class Meta:
        ordering = ['scheduled_time', 'id']
        constraints = [
            models.UniqueConstraint(fields=['stop', 'activity'], name='unique_activity_per_stop'),
        ]
        indexes = [
            models.Index(fields=['stop']),
        ]

    def __str__(self):
        return f"{self.activity.name} @ {self.stop}"
