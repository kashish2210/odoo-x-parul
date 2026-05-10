from django.urls import path
from . import views

app_name = 'checklists'

urlpatterns = [
    path('', views.checklist_view, name='checklist'),
    path('add/', views.add_item, name='add_item'),
    path('toggle/<int:item_id>/', views.toggle_item, name='toggle_item'),
    path('reset/', views.reset_checklist, name='reset_checklist'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
]
