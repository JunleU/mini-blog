"""用户模块 URL 路由（M01）。

URL 前缀：/accounts/
"""

from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password/', views.change_password, name='change_password'),
]
