from django.urls import path

from .views import AddActivityToStopView, ActivitySearchView, RemoveActivityFromStopView

app_name = 'destinations'

urlpatterns = [
    path('activities/', ActivitySearchView.as_view(), name='activity-search'),
    path('activities/add/', AddActivityToStopView.as_view(), name='activity-add'),
    path('activities/remove/', RemoveActivityFromStopView.as_view(), name='activity-remove'),
]