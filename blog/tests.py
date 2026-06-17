"""博客模块单元测试（UC03/UC04/UC05/UC06）。"""

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from blog.models import Article, Category


class ArticleModelTest(TestCase):
    """Article 模型与摘要逻辑测试。"""

    def setUp(self):
        self.author = User.objects.create_user(username='author', password='Author2024pw')
        self.article = Article.objects.create(
            title='测试标题', content='# 标题\n\n正文内容', author=self.author
        )

    def test_excerpt_generation(self):
        """excerpt 属性能去除 Markdown 符号并截断。"""
        excerpt = self.article.excerpt
        self.assertNotIn('#', excerpt)
        self.assertLessEqual(len(excerpt), 153)  # 150 + 省略号

    def test_default_status_published(self):
        """新文章默认状态为 published。"""
        self.assertEqual(self.article.status, Article.Status.PUBLISHED)

    def test_str_representation(self):
        """__str__ 返回标题。"""
        self.assertEqual(str(self.article), '测试标题')


class ArticleCRUDViewTest(TestCase):
    """文章增删改查视图测试（UC03-UC06）。"""

    def setUp(self):
        self.author = User.objects.create_user(username='author', password='Author2024pw')
        self.other = User.objects.create_user(username='other', password='Other2024pw')
        self.admin = User.objects.create_user(
            username='admin', password='Admin2024pw', role=User.Role.ADMIN
        )
        self.article = Article.objects.create(
            title='我的文章', content='内容', author=self.author
        )

    # ---- UC06 浏览 ----
    def test_index_shows_published_articles(self):
        """首页展示已发布文章。"""
        r = self.client.get(reverse('blog:index'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '我的文章')

    def test_index_hides_drafts(self):
        """首页不展示草稿。"""
        Article.objects.create(
            title='草稿文章', content='x', author=self.author, status=Article.Status.DRAFT
        )
        r = self.client.get(reverse('blog:index'))
        self.assertNotContains(r, '草稿文章')

    def test_article_detail_renders_markdown(self):
        """详情页渲染 Markdown。"""
        a = Article.objects.create(
            title='MD', content='**加粗**', author=self.author
        )
        r = self.client.get(reverse('blog:article_detail', kwargs={'pk': a.pk}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '<strong>加粗</strong>')

    def test_nonexistent_article_404(self):
        """不存在的文章返回 404。"""
        r = self.client.get(reverse('blog:article_detail', kwargs={'pk': 99999}))
        self.assertEqual(r.status_code, 404)

    # ---- UC03 发表 ----
    def test_create_requires_login(self):
        """未登录不能发表文章。"""
        r = self.client.get(reverse('blog:article_create'))
        self.assertEqual(r.status_code, 302)  # 重定向登录

    def test_create_article_when_logged_in(self):
        """登录用户可发表文章，作者自动关联。"""
        self.client.login(username='author', password='Author2024pw')
        r = self.client.post(reverse('blog:article_create'), {
            'title': '新文章', 'content': '正文', 'status': 'published'
        })
        self.assertEqual(r.status_code, 302)
        new = Article.objects.get(title='新文章')
        self.assertEqual(new.author, self.author)

    def test_empty_title_rejected(self):
        """空标题被拒。"""
        self.client.login(username='author', password='Author2024pw')
        r = self.client.post(reverse('blog:article_create'), {
            'title': '', 'content': '正文', 'status': 'published'
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Article.objects.filter(title='').exists())

    # ---- UC04 修改 ----
    def test_author_can_edit_own_article(self):
        """作者可修改自己的文章。"""
        self.client.login(username='author', password='Author2024pw')
        r = self.client.post(reverse('blog:article_update', kwargs={'pk': self.article.pk}), {
            'title': '修改后', 'content': '新内容', 'status': 'published'
        })
        self.assertEqual(r.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, '修改后')

    def test_non_author_cannot_edit(self):
        """非作者不能修改他人文章（403）。"""
        self.client.login(username='other', password='Other2024pw')
        r = self.client.post(reverse('blog:article_update', kwargs={'pk': self.article.pk}), {
            'title': '恶意修改', 'content': 'x', 'status': 'published'
        })
        self.assertEqual(r.status_code, 403)

    def test_admin_can_edit_any_article(self):
        """管理员可修改任意文章。"""
        self.client.login(username='admin', password='Admin2024pw')
        r = self.client.post(reverse('blog:article_update', kwargs={'pk': self.article.pk}), {
            'title': '管理员改的', 'content': 'x', 'status': 'published'
        })
        self.assertEqual(r.status_code, 302)

    # ---- UC05 删除 ----
    def test_author_can_delete_own_article(self):
        """作者可删除自己的文章。"""
        self.client.login(username='author', password='Author2024pw')
        r = self.client.post(reverse('blog:article_delete', kwargs={'pk': self.article.pk}))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Article.objects.filter(pk=self.article.pk).exists())

    def test_non_author_cannot_delete(self):
        """非作者不能删除他人文章。"""
        self.client.login(username='other', password='Other2024pw')
        r = self.client.post(reverse('blog:article_delete', kwargs={'pk': self.article.pk}))
        self.assertEqual(r.status_code, 403)


class CategoryTest(TestCase):
    """分类功能测试。"""

    def setUp(self):
        self.author = User.objects.create_user(username='a', password='Author2024pw')
        self.cat = Category.objects.create(name='技术', description='技术类')

    def test_category_filter(self):
        """按分类筛选文章。"""
        Article.objects.create(title='T1', content='x', author=self.author, category=self.cat)
        r = self.client.get(reverse('blog:category', kwargs={'pk': self.cat.pk}))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'T1')

    def test_category_unique_name(self):
        """分类名唯一。"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='技术')
