from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    """后台管理模块配置（M04）。参见 SAD §4.1.1。

    与 Django 内置 admin 不同，本模块提供面向管理员角色的
    独立后台管理界面（用户/文章/评论的查询、修改、删除）。
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel'
    verbose_name = '后台管理'
