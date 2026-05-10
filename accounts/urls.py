from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Static Footer Pages
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('careers/', views.careers_view, name='careers'),
    path('help/', views.help_view, name='help'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    
    path('admin-panel/login/', views.admin_panel_login_view, name='admin_panel_login'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('', views.dashboard_view, name='dashboard'),
]
