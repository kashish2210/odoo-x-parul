from django.contrib import admin
from .models import Trip, Stop, StopActivity


class StopInline(admin.TabularInline):
    model = Stop
    extra = 1


class StopActivityInline(admin.TabularInline):
    model = StopActivity
    extra = 1


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'start_date', 'end_date', 'is_public')
    list_filter = ('is_public', 'start_date')
    search_fields = ('name', 'user__username')
    inlines = [StopInline]


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ('trip', 'city', 'arrival_date', 'departure_date', 'order')
    list_filter = ('city__country',)
    inlines = [StopActivityInline]


@admin.register(StopActivity)
class StopActivityAdmin(admin.ModelAdmin):
    list_display = ('activity', 'stop', 'scheduled_time')
