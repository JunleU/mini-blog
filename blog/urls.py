"""博客模块 URL 路由（M02）。

URL 前缀：/  （项目根，博客为首页）
"""

from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # UC06 浏览文章
    path('', views.IndexView.as_view(), name='index'),
    path('article/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('category/<int:pk>/', views.CategoryListView.as_view(), name='category'),
    # UC03/UC04/UC05 文章管理
    path('article/new/', views.ArticleCreateView.as_view(), name='article_create'),
    path('article/<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('article/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
]
