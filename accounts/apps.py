from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """用户模块配置（M01）。参见 SAD §4.1.1。"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = '用户管理'

    def ready(self):
        # 导入信号处理器：User 创建/保存时同步关联数据
        # （将在实现 accounts 模块时启用）
        try:
            from . import signals  # noqa: F401
        except ImportError:
            pass
