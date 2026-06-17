"""后台管理模块单元测试（UC08/UC09/UC10）。"""

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from blog.models import Article
from comments.models import Comment


class AdminPanelAccessTest(TestCase):
    """后台管理权限测试。"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='Admin2024pw', role=User.Role.ADMIN
        )
        self.normal = User.objects.create_user(username='normal', password='Normal2024pw')

    def test_anonymous_redirected_to_login(self):
        """匿名用户访问后台被重定向到登录。"""
        r = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(r.status_code, 302)

    def test_normal_user_forbidden(self):
        """普通用户访问后台被拒（403）。"""
        self.client.login(username='normal', password='Normal2024pw')
        r = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(r.status_code, 403)

    def test_admin_can_access_dashboard(self):
        """管理员可访问仪表盘。"""
        self.client.login(username='admin', password='Admin2024pw')
        r = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '仪表盘')


class UserManagementTest(TestCase):
    """UC08 用户管理测试。"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='Admin2024pw', role=User.Role.ADMIN
        )
        self.target = User.objects.create_user(username='target', password='Target2024pw')
        self.client.login(username='admin', password='Admin2024pw')

    def test_user_list(self):
        """用户列表可访问且含数据。"""
        r = self.client.get(reverse('admin_panel:user_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'target')

    def test_user_search(self):
        """用户搜索功能。"""
        r = self.client.get(reverse('admin_panel:user_list') + '?q=target')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'target')

    def test_edit_user_role(self):
        """管理员可修改用户角色。"""
        r = self.client.post(reverse('admin_panel:user_edit', kwargs={'pk': self.target.pk}), {
            'role': 'admin', 'is_active': True, 'email': 't@t.com', 'bio': ''
        })
        self.assertEqual(r.status_code, 302)
        self.target.refresh_from_db()
        self.assertEqual(self.target.role, User.Role.ADMIN)

    def test_toggle_user_active(self):
        """管理员可禁用/启用用户。"""
        r = self.client.post(reverse('admin_panel:user_toggle', kwargs={'pk': self.target.pk}))
        self.assertEqual(r.status_code, 302)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_active)

    def test_delete_user(self):
        """管理员可删除用户（级联删除文章评论）。"""
        Article.objects.create(title='x', content='y', author=self.target)
        r = self.client.post(reverse('admin_panel:user_delete', kwargs={'pk': self.target.pk}))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.target.pk).exists())
        self.assertEqual(Article.objects.count(), 0)

    def test_cannot_delete_self(self):
        """管理员不能删除自己。"""
        r = self.client.post(reverse('admin_panel:user_delete', kwargs={'pk': self.admin.pk}))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())


class ArticleManagementTest(TestCase):
    """UC09 文章管理测试。"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='Admin2024pw', role=User.Role.ADMIN
        )
        self.author = User.objects.create_user(username='author', password='Author2024pw')
        self.article = Article.objects.create(title='T', content='C', author=self.author)
        self.client.login(username='admin', password='Admin2024pw')

    def test_article_list(self):
        r = self.client.get(reverse('admin_panel:article_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'T')

    def test_edit_any_article(self):
        """管理员可修改任意文章。"""
        r = self.client.post(reverse('admin_panel:article_edit', kwargs={'pk': self.article.pk}), {
            'title': '改后', 'content': '新', 'status': 'draft'
        })
        self.assertEqual(r.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, '改后')
        self.assertEqual(self.article.status, Article.Status.DRAFT)

    def test_delete_article(self):
        """管理员可删除任意文章。"""
        r = self.client.post(reverse('admin_panel:article_delete', kwargs={'pk': self.article.pk}))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Article.objects.filter(pk=self.article.pk).exists())


class CommentManagementTest(TestCase):
    """UC10 评论管理测试。"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', password='Admin2024pw', role=User.Role.ADMIN
        )
        self.author = User.objects.create_user(username='author', password='Author2024pw')
        self.article = Article.objects.create(title='T', content='C', author=self.author)
        self.comment = Comment.objects.create(
            content='评论', author=self.author, article=self.article
        )
        self.client.login(username='admin', password='Admin2024pw')

    def test_comment_list(self):
        r = self.client.get(reverse('admin_panel:comment_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '评论')

    def test_delete_comment(self):
        r = self.client.post(reverse('admin_panel:comment_delete', kwargs={'pk': self.comment.pk}))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())
