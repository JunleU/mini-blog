from django.apps import AppConfig


class BlogConfig(AppConfig):
    """博客模块配置（M02）。参见 SAD §4.1.1。"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = '博客文章'
