"""评论模块 Django Admin 注册。"""

from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'article', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username', 'article__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    raw_id_fields = ('author', 'article')
