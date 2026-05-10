from django.urls import path
from . import views

urlpatterns = [
    path('', views.trip_list_view, name='trip_list'),
    path('create/', views.trip_create_view, name='trip_create'),
    path('explore/', views.explore_view, name='explore'),
    path('<int:trip_id>/', views.trip_detail_view, name='trip_detail'),
    path('<int:trip_id>/edit/', views.trip_edit_view, name='trip_edit'),
    path('<int:trip_id>/delete/', views.trip_delete_view, name='trip_delete'),
    path('<int:trip_id>/itinerary/', views.trip_itinerary_view, name='trip_itinerary'),
    path('<int:trip_id>/stops/<int:stop_id>/delete/', views.stop_delete_view, name='stop_delete'),
]
