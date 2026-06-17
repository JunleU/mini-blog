"""用户模块数据模型（M01）。

定义自定义用户模型 User，扩展 Django 内置 AbstractUser，
新增 role（角色）、bio（个人简介）、avatar（头像 URL）字段。

依据：SAD §4.2.4 User；SRS §3.6 数据字典。
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """系统用户模型。

    继承 AbstractUser 获得 username / password / email / date_joined /
    is_active / is_staff 等标准字段，并扩展：
      - role：角色（author 普通作者 / admin 系统管理员）
      - bio：个人简介
      - avatar：头像 URL（采用 URLField 而非 ImageField，避免 Pillow
        等二进制依赖；存储外部头像链接或静态资源路径）

    密码以 PBKDF2 + SHA256 哈希加盐存储（Django 默认），不保存明文。
    """

    class Role(models.TextChoices):
        AUTHOR = 'author', '普通用户'
        ADMIN = 'admin', '管理员'

    # 角色：默认普通用户，管理员通过后台或标记提升
    role = models.CharField(
        '角色', max_length=10, choices=Role.choices, default=Role.AUTHOR
    )
    bio = models.CharField('个人简介', max_length=500, blank=True, default='')
    avatar = models.URLField('头像 URL', max_length=500, blank=True, default='')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    # ---- 便捷属性 ----
    @property
    def is_admin_role(self):
        """是否为管理员角色（区别于 Django 内置 is_staff/is_superuser）。"""
        return self.role == self.Role.ADMIN
