from django.urls import path
from . import views

urlpatterns = [
    path('fetch-restaurants/', views.fetch_restaurants, name='fetch_restaurants'),
    path('', views.show_map, name='show_map'),
]