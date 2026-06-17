"""博客模块数据模型（M02）。

定义文章分类 Category 与文章 Article。

依据：SAD §4.2 Article / Category；SRS §3.6 数据字典。
"""

from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """文章分类。

    分类名唯一（SRS：Category.name UNIQUE, NOT NULL），用于对文章归类。
    """

    name = models.CharField('分类名称', max_length=50, unique=True)
    description = models.CharField('分类描述', max_length=200, blank=True, default='')

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):
    """博客文章。

    字段对应 SAD §4.2 Article：
      - title：标题（CharField(200)）
      - content：正文，Markdown 格式（TextField）
      - created_at：创建时间（auto_now_add）
      - updated_at：最后修改时间（auto_now）
      - status：状态 draft(草稿) / published(已发布)
      - author：作者外键，级联删除
      - category：分类外键，可为空，分类删除时置空（SET NULL）
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PUBLISHED = 'published', '已发布'

    title = models.CharField('标题', max_length=200)
    content = models.TextField('正文（Markdown）')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    status = models.CharField(
        '状态', max_length=10, choices=Status.choices, default=Status.PUBLISHED
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name='作者',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name='分类',
    )

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """文章详情页绝对 URL。"""
        return reverse('blog:article_detail', kwargs={'pk': self.pk})

    @property
    def excerpt(self):
        """文章摘要：截取正文前 150 个字符（去除 Markdown 标记后）。"""
        import re
        plain = re.sub(r'[#*`>\-_~\[\]\(\)!]', '', self.content)
        plain = re.sub(r'\s+', ' ', plain).strip()
        return plain[:150] + ('…' if len(plain) > 150 else '')
