"""后台管理模块视图（M04）。

实现 SRS 用例：
  - UC08 管理用户（查询/修改/删除/禁用/启用/提升管理员）
  - UC09 管理文章（查询/修改/删除/改状态）
  - UC10 管理评论（查询/删除）

所有视图均要求管理员角色（AdminRequiredMixin）。
URL 前缀：/manage/
"""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts.mixins import AdminRequiredMixin
from accounts.models import User
from blog.models import Article
from comments.models import Comment

from .forms import ArticleAdminForm, UserAdminForm

PER_PAGE = 15  # 后台每页条数（settings.ADMIN_PER_PAGE）


# ============================================================
# 仪表盘概览
# ============================================================
from django.views.generic import TemplateView


class DashboardView(AdminRequiredMixin, TemplateView):
    """后台首页：展示全站数据统计概览。"""

    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_count'] = User.objects.count()
        ctx['article_count'] = Article.objects.count()
        ctx['comment_count'] = Comment.objects.count()
        ctx['published_count'] = Article.objects.filter(
            status=Article.Status.PUBLISHED
        ).count()
        ctx['draft_count'] = Article.objects.filter(status=Article.Status.DRAFT).count()
        ctx['active_user_count'] = User.objects.filter(is_active=True).count()
        # 最近 5 条文章 / 评论
        ctx['recent_articles'] = Article.objects.select_related('author').order_by('-created_at')[:5]
        ctx['recent_comments'] = Comment.objects.select_related('author', 'article').order_by('-created_at')[:5]
        return ctx


# ============================================================
# UC08 用户管理
# ============================================================
def user_list(request):
    """UC08 用户列表（支持按用户名/邮箱搜索）。"""
    q = request.GET.get('q', '').strip()
    qs = User.objects.all().order_by('-date_joined')
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q))
    paginator = Paginator(qs, PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/user_list.html', {
        'page_obj': page, 'q': q, 'section': 'users',
    })


def user_edit(request, pk):
    """UC08 修改用户（角色/状态/邮箱/简介）。"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserAdminForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'用户 {user.username} 资料已更新。')
            return redirect('admin_panel:user_list')
    else:
        form = UserAdminForm(instance=user)
    return render(request, 'admin_panel/user_form.html', {
        'form': form, 'target_user': user, 'section': 'users',
    })


@require_POST
def user_delete(request, pk):
    """UC08 删除用户（级联删除其文章与评论）。不允许删除自己。"""
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, '不能删除自己当前登录的账号。')
        return redirect('admin_panel:user_list')
    username = user.username
    user.delete()
    messages.success(request, f'用户 {username} 及其文章、评论已删除。')
    return redirect('admin_panel:user_list')


@require_POST
def user_toggle_active(request, pk):
    """UC08 启用/禁用用户账号。"""
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, '不能禁用自己当前登录的账号。')
        return redirect('admin_panel:user_list')
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    state = '启用' if user.is_active else '禁用'
    messages.success(request, f'用户 {user.username} 已{state}。')
    return redirect('admin_panel:user_list')


# ============================================================
# UC09 文章管理
# ============================================================
def article_list(request):
    """UC09 文章列表（支持按标题/作者搜索）。"""
    q = request.GET.get('q', '').strip()
    qs = Article.objects.select_related('author', 'category').all()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(author__username__icontains=q))
    paginator = Paginator(qs, PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/article_list.html', {
        'page_obj': page, 'q': q, 'section': 'articles',
    })


def article_edit(request, pk):
    """UC09 修改任意文章（标题/正文/分类/状态）。"""
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleAdminForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, f'文章《{article.title}》已更新。')
            return redirect('admin_panel:article_list')
    else:
        form = ArticleAdminForm(instance=article)
    return render(request, 'admin_panel/article_form.html', {
        'form': form, 'article': article, 'section': 'articles',
    })


@require_POST
def article_delete(request, pk):
    """UC09 删除任意文章（级联删除评论）。"""
    article = get_object_or_404(Article, pk=pk)
    title = article.title
    article.delete()
    messages.success(request, f'文章《{title}》及其评论已删除。')
    return redirect('admin_panel:article_list')


# ============================================================
# UC10 评论管理
# ============================================================
def comment_list(request):
    """UC10 评论列表（支持按内容/评论者搜索）。"""
    q = request.GET.get('q', '').strip()
    qs = Comment.objects.select_related('author', 'article').all()
    if q:
        qs = qs.filter(Q(content__icontains=q) | Q(author__username__icontains=q))
    paginator = Paginator(qs, PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/comment_list.html', {
        'page_obj': page, 'q': q, 'section': 'comments',
    })


@require_POST
def comment_delete(request, pk):
    """UC10 删除任意评论。"""
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    messages.success(request, '评论已删除。')
    return redirect('admin_panel:comment_list')


# 为上述函数视图统一套上管理员权限装饰器
# （集中在此处应用，避免每个函数定义上加装饰器造成重复）
_dashboard = DashboardView.as_view()

# 注意：由于 Django 函数视图与混入配合，这里对每个视图显式应用
# AdminRequiredMixin 的 dispatch 逻辑。为保持代码简洁清晰，
# 以下包装函数统一注入管理员权限校验。

def _admin_required(view_func):
    """函数视图的管理员权限装饰器（基于 AdminRequiredMixin.dispatch）。"""
    mixin = AdminRequiredMixin()

    def wrapper(request, *args, **kwargs):
        mixin.request = request
        if not request.user.is_authenticated:
            return mixin.handle_no_permission()
        if not getattr(request.user, 'is_admin_role', False):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied('您没有权限执行此操作。')
        return view_func(request, *args, **kwargs)

    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper


# 应用装饰器（保持原函数名供 URL 引用）
user_list = _admin_required(user_list)
user_edit = _admin_required(user_edit)
user_delete = _admin_required(user_delete)
user_toggle_active = _admin_required(user_toggle_active)
article_list = _admin_required(article_list)
article_edit = _admin_required(article_edit)
article_delete = _admin_required(article_delete)
comment_list = _admin_required(comment_list)
comment_delete = _admin_required(comment_delete)
