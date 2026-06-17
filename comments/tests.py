"""评论模块单元测试（UC07）。"""

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from blog.models import Article
from comments.models import Comment


class CommentTest(TestCase):
    """UC07 评论提交/展示/删除测试。"""

    def setUp(self):
        self.author = User.objects.create_user(username='author', password='Author2024pw')
        self.commenter = User.objects.create_user(username='commenter', password='Commenter2024pw')
        self.other = User.objects.create_user(username='other', password='Other2024pw')
        self.article = Article.objects.create(
            title='文章', content='内容', author=self.author
        )

    def test_create_comment_requires_login(self):
        """未登录不能评论。"""
        r = self.client.post(reverse('comments:create', kwargs={'article_id': self.article.pk}),
                             {'content': '评论'})
        self.assertEqual(r.status_code, 302)  # 重定向登录

    def test_create_comment_when_logged_in(self):
        """登录用户可发表评论。"""
        self.client.login(username='commenter', password='Commenter2024pw')
        r = self.client.post(reverse('comments:create', kwargs={'article_id': self.article.pk}),
                             {'content': '好文章！'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Comment.objects.filter(content='好文章！').exists())

    def test_empty_comment_rejected(self):
        """空评论被拒。"""
        self.client.login(username='commenter', password='Commenter2024pw')
        r = self.client.post(reverse('comments:create', kwargs={'article_id': self.article.pk}),
                             {'content': ''})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Comment.objects.exists())

    def test_comment_shown_on_article_page(self):
        """评论展示在文章详情页。"""
        Comment.objects.create(content='显示我', author=self.commenter, article=self.article)
        r = self.client.get(reverse('blog:article_detail', kwargs={'pk': self.article.pk}))
        self.assertContains(r, '显示我')

    def test_xss_script_stripped(self):
        """评论中的 script 标签被剥离（XSS 防护）。"""
        self.client.login(username='commenter', password='Commenter2024pw')
        self.client.post(reverse('comments:create', kwargs={'article_id': self.article.pk}),
                         {'content': '<script>alert(1)</script>正常'})
        r = self.client.get(reverse('blog:article_detail', kwargs={'pk': self.article.pk}))
        self.assertNotContains(r, '<script>')

    def test_author_can_delete_own_comment(self):
        """评论者可删除自己的评论。"""
        c = Comment.objects.create(content='我的', author=self.commenter, article=self.article)
        self.client.login(username='commenter', password='Commenter2024pw')
        r = self.client.post(reverse('comments:delete', kwargs={'pk': c.pk}))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=c.pk).exists())

    def test_non_author_cannot_delete_comment(self):
        """非评论者不能删除他人评论。"""
        c = Comment.objects.create(content='别人的', author=self.commenter, article=self.article)
        self.client.login(username='other', password='Other2024pw')
        r = self.client.post(reverse('comments:delete', kwargs={'pk': c.pk}))
        self.assertEqual(r.status_code, 403)

    def test_cascade_delete_with_article(self):
        """文章删除时评论级联删除。"""
        Comment.objects.create(content='c1', author=self.commenter, article=self.article)
        self.article.delete()
        self.assertEqual(Comment.objects.count(), 0)
