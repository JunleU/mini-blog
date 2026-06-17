"""用户模块 Django Admin 注册。

将自定义 User 模型注册到 Django 内置 admin（路径 /dj-admin/），
提供补充管理手段。主管理界面由 admin_panel 模块提供。
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户在 Django Admin 中的展示。"""

    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('role', 'bio', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('扩展信息', {'fields': ('role', 'bio', 'avatar')}),
    )
