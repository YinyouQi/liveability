from django.urls import path
from . import views

app_name = 'liveability'
urlpatterns = [
    path('', views.index, name='index'),
    path('fetch/<str:city_name>/', views.fetch_city),
    path('dashboard/<str:city1>/<str:city2>/', views.city_dashboard, name='dashboard'),
    path('methodology/', views.methodology, name='methodology'),

    # 收藏功能相关路由
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('favorites/add/<str:city_name>/', views.add_favorite, name='add_favorite'),
    path('favorites/remove/<str:city_name>/', views.remove_favorite, name='remove_favorite'),
]