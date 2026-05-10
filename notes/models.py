from django.conf import settings
from django.db import models


class StubTrip(models.Model):
    """
    Kept only so the initial migration (0001) remains valid.
    New notes use the real Trip from the trips app.
    Do NOT create new StubTrip objects — use trips.Trip instead.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stub_trips')
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Trip (Stub — deprecated)'
        verbose_name_plural = 'Trips (Stub — deprecated)'

    def __str__(self):
        return self.name


class Note(models.Model):
    """A text note tied to a real Trip and optionally a specific stop or day."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    trip = models.ForeignKey(
        'trips.Trip',
        on_delete=models.CASCADE,
        related_name='trip_journal_notes',
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    stop_name = models.CharField(
        max_length=150,
        blank=True,
        help_text='e.g. Rome stop, Paris stop'
    )
    day_label = models.CharField(
        max_length=100,
        blank=True,
        help_text='e.g. Day 3: June 14 2025'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        return self.title
