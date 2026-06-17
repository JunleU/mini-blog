"""博客模块 Django Admin 注册。"""

from django.contrib import admin
from django.db.models import Count

from .models import Article, Category


class ArticleInline(admin.TabularInline):
    """分类详情页内嵌的文章列表。"""
    model = Article
    extra = 0
    readonly_fields = ('title', 'author', 'created_at')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'num_articles')
    search_fields = ('name',)
    inlines = [ArticleInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _num_articles=Count('articles')
        )

    def num_articles(self, obj):
        return obj.articles.count()
    num_articles.short_description = '文章数'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'category', 'author')
    search_fields = ('title', 'content', 'author__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('author',)
