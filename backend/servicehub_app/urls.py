from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('api/nearby-providers/', views.find_nearby_providers, name='nearby_providers'),
    path('api/book/<int:provider_id>/', views.create_booking, name='create_booking'),
    path('api/my-bookings/', views.get_my_bookings, name='my_bookings'),
    path('dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('apply/', views.apply_provider, name='apply_provider'), # New custom form path
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='servicehub_app/login.html'), name='login'),
]