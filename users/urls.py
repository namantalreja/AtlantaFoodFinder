
from django.urls import path
from .views import home, RegisterView, ResetPasswordView  # Import the view here
from django.contrib.auth import views as auth_views
from .views import profile
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),  # This is what we added
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('profile/', profile, name='users-profile'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('restaurant-details/<str:place_id>/', views.restaurant_details, name='restaurant_details'),
    path('fetch-restaurants/', views.fetch_restaurants, name='fetch_restaurants'),
    path('map/', views.show_map, name='show_map'),
]
