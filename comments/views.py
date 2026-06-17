"""评论模块视图（M03）。

实现 SRS 用例：
  - UC07 发表评论（comment_create，嵌入文章详情页）
  - 评论删除（comment_delete，仅评论者本人或管理员）
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from blog.models import Article

from .forms import CommentForm
from .models import Comment


@require_POST
@login_required
def comment_create(request, article_id):
    """UC07 发表评论。

    接收文章 id 与评论内容，关联当前用户，写入 Comment 表后
    重定向回文章详情页（评论展示在末尾）。
    """
    article = get_object_or_404(Article, pk=article_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.author = request.user
        comment.save()
        messages.success(request, '评论发表成功。')
    else:
        # 把表单错误通过消息框架回显
        for errors in form.errors.values():
            for err in errors:
                messages.error(request, err)
    # 回到详情页评论锚点
    return redirect(reverse('blog:article_detail', kwargs={'pk': article.pk}) + '#comments')


@login_required
def comment_delete(request, pk):
    """评论删除（仅评论者本人或管理员）。

    GET  → 渲染确认页面。
    POST → 执行删除。
    """
    comment = get_object_or_404(Comment, pk=pk)
    user = request.user
    # 权限校验：仅评论者本人或管理员可删除
    if comment.author != user and not getattr(user, 'is_admin_role', False):
        raise PermissionDenied('您没有权限执行此操作。')

    if request.method == 'POST':
        article_pk = comment.article_id
        comment.delete()
        messages.success(request, '评论已删除。')
        return redirect(reverse('blog:article_detail', kwargs={'pk': article_pk}) + '#comments')

    return render(request, 'comments/comment_confirm_delete.html', {'comment': comment})
