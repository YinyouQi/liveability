from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('fetch/<str:city_name>/', views.fetch_city),
]