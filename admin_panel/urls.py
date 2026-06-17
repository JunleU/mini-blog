"""后台管理模块 URL 路由（M04）。

URL 前缀：/manage/
所有视图要求管理员角色。
"""

from django.urls import path

from . import views

app_name = 'admin_panel'

urlpatterns = [
    # 仪表盘
    path('', views.DashboardView.as_view(), name='dashboard'),
    # UC08 用户管理
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle'),
    # UC09 文章管理
    path('articles/', views.article_list, name='article_list'),
    path('articles/<int:pk>/edit/', views.article_edit, name='article_edit'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),
    # UC10 评论管理
    path('comments/', views.comment_list, name='comment_list'),
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
]
