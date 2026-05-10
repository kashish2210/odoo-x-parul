from django.contrib import admin
from .models import City, Activity


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'region', 'cost_index', 'popularity_score')
    list_filter = ('country', 'region')
    search_fields = ('name', 'country')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'category', 'estimated_cost', 'duration_minutes')
    list_filter = ('category', 'city__country')
    search_fields = ('name', 'city__name')
