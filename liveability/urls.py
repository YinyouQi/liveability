from django.urls import path
from . import views

app_name = 'liveability'
urlpatterns = [
    path('', views.index, name='index'),
    path('fetch/<str:city_name>/', views.fetch_city),
    path('dashboard/<str:city1>/<str:city2>/', views.city_dashboard, name='dashboard'),
]