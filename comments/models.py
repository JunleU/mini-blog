"""评论模块数据模型（M03）。

定义评论 Comment，关联作者与文章。

依据：SAD §4.2 Comment；SRS §3.6 数据字典。
"""

from django.conf import settings
from django.db import models


class Comment(models.Model):
    """评论实体。

    字段对应 SAD §4.2 Comment：
      - content：评论内容（TextField）
      - created_at：评论时间（auto_now_add）
      - author：评论者外键，级联删除（用户删除时评论一并删除）
      - article：所属文章外键，级联删除（文章删除时评论一并删除）
    """

    content = models.TextField('评论内容', max_length=2000)
    created_at = models.DateTimeField('评论时间', auto_now_add=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='评论者',
    )
    article = models.ForeignKey(
        'blog.Article',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='所属文章',
    )

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']  # 评论按时间升序（SRS UC06）

    def __str__(self):
        # 展示评论者与内容摘要
        preview = self.content[:20] + ('…' if len(self.content) > 20 else '')
        return f'{self.author.username}: {preview}'
