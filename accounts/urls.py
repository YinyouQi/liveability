from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # 登录页面
    path('login/', 
         auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # 注销
    path('logout/', 
         auth_views.LogoutView.as_view(), name='logout'),
    
    # 包含默认的⾝份验证 URL
    path('', include('django.contrib.auth.urls')),
    
    # 注册
    path('register/', views.register, name='register'),
]