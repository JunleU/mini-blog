from django.apps import AppConfig


class CommentsConfig(AppConfig):
    """评论模块配置（M03）。参见 SAD §4.1.1。"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comments'
    verbose_name = '评论互动'
