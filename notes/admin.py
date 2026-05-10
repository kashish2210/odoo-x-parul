from django.contrib import admin
from .models import Note, StubTrip


@admin.register(StubTrip)
class StubTripAdmin(admin.ModelAdmin):
    """Deprecated stub — kept for migration history only."""
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip', 'user', 'stop_name', 'day_label', 'updated_at')
    search_fields = ('title', 'content', 'stop_name', 'user__username', 'trip__name')
    list_filter = ('trip', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
