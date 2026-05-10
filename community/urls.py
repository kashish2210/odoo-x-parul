from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.community_list_view, name='community_list'),
    path('create/', views.community_create_view, name='community_create'),
    path('<int:post_id>/', views.community_detail_view, name='community_detail'),
    path('<int:post_id>/like/', views.community_like_view, name='community_like'),
    path('<int:post_id>/delete/', views.community_delete_view, name='community_delete'),
]
