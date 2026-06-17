"""评论模块 URL 路由（M03）。

URL 前缀：/comments/
"""

from django.urls import path

from . import views

app_name = 'comments'

urlpatterns = [
    # UC07 发表评论：POST /comments/<article_id>/create/
    path('<int:article_id>/create/', views.comment_create, name='create'),
    # 评论删除
    path('<int:pk>/delete/', views.comment_delete, name='delete'),
]
