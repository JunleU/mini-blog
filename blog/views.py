"""博客模块视图（M02）。

实现 SRS 用例：
  - UC06 浏览文章（index 列表页 + article_detail 详情页 + category 分类页）
  - UC03 发表文章（article_create）
  - UC04 修改文章（article_update）
  - UC05 删除文章（article_delete）
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from accounts.mixins import OwnerOrAdminRequiredMixin

from .forms import ArticleForm
from .markdown_utils import render_markdown
from .models import Article, Category


def get_categories_with_counts():
    """获取所有分类及其文章数，用于侧边栏。"""
    return Category.objects.annotate(num_articles=Count('articles'))


class IndexView(ListView):
    """UC06 文章列表页（首页）。

    展示已发布文章，按更新时间降序，每页 ARTICLES_PER_PAGE 条。
    """

    model = Article
    template_name = 'blog/index.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.filter(status=Article.Status.PUBLISHED).select_related(
            'author', 'category'
        )
        # 支持搜索（可选扩展功能）
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(title__icontains=q)
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = get_categories_with_counts()
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class ArticleDetailView(DetailView):
    """UC06 文章详情页。

    展示文章全文（Markdown 渲染为安全 HTML）及其评论列表。
    """

    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        # 详情页允许查看草稿（仅作者/管理员），其余仅看已发布
        user = self.request.user
        if not user.is_authenticated:
            qs = Article.objects.filter(status=Article.Status.PUBLISHED)
        elif user.is_admin_role:
            qs = Article.objects.all()
        else:
            # 非管理员：已发布 或 自己写的草稿
            qs = Article.objects.filter(status=Article.Status.PUBLISHED) | \
                 Article.objects.filter(author=user, status=Article.Status.DRAFT)
            qs = qs.distinct()
        return qs.select_related('author', 'category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        # 渲染 Markdown 正文（XSS 过滤）
        ctx['rendered_content'] = render_markdown(article.content)
        # 评论按时间升序（SRS UC06）
        ctx['comments'] = article.comments.select_related('author').all()
        ctx['categories'] = get_categories_with_counts()
        return ctx


class CategoryListView(ListView):
    """按分类筛选的文章列表。"""

    model = Article
    template_name = 'blog/index.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        return Article.objects.filter(
            category=self.category, status=Article.Status.PUBLISHED
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = get_categories_with_counts()
        ctx['current_category'] = self.category
        return ctx


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """UC03 发表文章（需登录）。"""

    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'

    def form_valid(self, form):
        # 关联当前登录用户为作者
        form.instance.author = self.request.user
        messages.success(self.request, '文章发表成功！')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_create'] = True
        return ctx


class ArticleUpdateView(OwnerOrAdminRequiredMixin, UpdateView):
    """UC04 修改文章（仅作者本人或管理员）。"""

    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'

    def get_queryset(self):
        return Article.objects.select_related('author')

    def form_valid(self, form):
        messages.success(self.request, '文章修改成功！')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_create'] = False
        return ctx


class ArticleDeleteView(OwnerOrAdminRequiredMixin, DeleteView):
    """UC05 删除文章（仅作者本人或管理员）。

    删除时级联删除其下所有评论（Django CASCADE 自动完成）。
    前端通过确认对话框二次确认。
    """

    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('blog:index')

    def get_queryset(self):
        return Article.objects.select_related('author')

    def form_valid(self, form):
        messages.success(self.request, '文章已删除。')
        return super().form_valid(form)
