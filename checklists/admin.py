from django.contrib import admin
from .models import PackingItem, TripNote


@admin.register(PackingItem)
class PackingItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'trip', 'category', 'is_packed')
    list_filter = ('category', 'is_packed')
    search_fields = ('name', 'trip__name')


@admin.register(TripNote)
class TripNoteAdmin(admin.ModelAdmin):
    list_display = ('trip', 'stop', 'created_at')
    list_filter = ('trip',)
    search_fields = ('content',)
