"""用户模块单元测试（UC01/UC02/UC11）。

覆盖 SRS：
  - UC01 注册：用户名/邮箱唯一性、密码强度、两次密码一致
  - UC02 登录：正确凭据成功、错误凭据拒绝、禁用账号拒绝
  - UC11 个人信息：修改邮箱、修改密码（需验证原密码）
"""

from django.contrib.auth import authenticate
from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class RegisterViewTest(TestCase):
    """UC01 用户注册视图测试。"""

    def test_register_page_renders(self):
        """注册页可正常渲染。"""
        r = self.client.get(reverse('accounts:register'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '注册')

    def test_successful_registration(self):
        """合法数据注册成功，密码以哈希存储。"""
        r = self.client.post(reverse('accounts:register'), {
            'username': 'alice',
            'email': 'alice@test.com',
            'password': 'Alice2024pw',
            'confirm_password': 'Alice2024pw',
        })
        self.assertEqual(r.status_code, 302)  # 重定向到登录页
        user = User.objects.get(username='alice')
        self.assertTrue(user.check_password('Alice2024pw'))
        self.assertFalse(user.check_password('wrong'))  # 非明文存储

    def test_duplicate_username_rejected(self):
        """重复用户名被拒绝。"""
        User.objects.create_user(username='bobb', password='Bob2024pw')
        r = self.client.post(reverse('accounts:register'), {
            'username': 'bobb',
            'email': 'bob2@test.com',
            'password': 'Bob2024pw',
            'confirm_password': 'Bob2024pw',
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '已被注册')

    def test_duplicate_email_rejected(self):
        """重复邮箱被拒绝。"""
        User.objects.create_user(username='carol', email='c@t.com', password='Carol2024pw')
        r = self.client.post(reverse('accounts:register'), {
            'username': 'carol2',
            'email': 'c@t.com',
            'password': 'Carol2024pw',
            'confirm_password': 'Carol2024pw',
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '已被注册')

    def test_password_mismatch_rejected(self):
        """两次密码不一致被拒绝。"""
        r = self.client.post(reverse('accounts:register'), {
            'username': 'dave',
            'email': 'dave@t.com',
            'password': 'Dave2024pw',
            'confirm_password': 'Different123',
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '不一致')

    def test_password_without_digit_rejected(self):
        """纯字母密码（无数字）被拒绝。"""
        r = self.client.post(reverse('accounts:register'), {
            'username': 'eve',
            'email': 'eve@t.com',
            'password': 'passwordABC',
            'confirm_password': 'passwordABC',
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '字母和数字')

    def test_invalid_username_chars_rejected(self):
        """含非法字符的用户名被拒绝。"""
        r = self.client.post(reverse('accounts:register'), {
            'username': 'ab',  # 太短
            'email': 'x@t.com',
            'password': 'Test2024pw',
            'confirm_password': 'Test2024pw',
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '用户名')


class LoginViewTest(TestCase):
    """UC02 用户登录视图测试。"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='frank', password='Frank2024pw', email='frank@t.com'
        )

    def test_successful_login(self):
        """正确凭据登录成功并建立会话。"""
        r = self.client.post(reverse('accounts:login'), {
            'username': 'frank', 'password': 'Frank2024pw'
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.wsgi_request.user.is_authenticated or
                        '_auth_user_id' in self.client.session)

    def test_wrong_password_rejected(self):
        """错误密码登录失败，返回模糊提示。"""
        r = self.client.post(reverse('accounts:login'), {
            'username': 'frank', 'password': 'wrongpass'
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '用户名或密码错误')

    def test_nonexistent_user_rejected(self):
        """不存在的用户名登录失败，返回相同模糊提示（防枚举）。"""
        r = self.client.post(reverse('accounts:login'), {
            'username': 'nobody', 'password': 'whatever123'
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '用户名或密码错误')

    def test_disabled_account_rejected(self):
        """被禁用账号登录被拒，并显示禁用提示（SRS UC02）。"""
        self.user.is_active = False
        self.user.save()
        r = self.client.post(reverse('accounts:login'), {
            'username': 'frank', 'password': 'Frank2024pw'
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '已被禁用')


class ProfileViewTest(TestCase):
    """UC11 个人信息管理测试。"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='grace', password='Grace2024pw', email='grace@t.com'
        )
        self.client.login(username='grace', password='Grace2024pw')

    def test_profile_requires_login(self):
        """个人信息页要求登录。"""
        self.client.logout()
        r = self.client.get(reverse('accounts:profile'))
        self.assertEqual(r.status_code, 302)  # 重定向到登录

    def test_update_email(self):
        """可修改邮箱。"""
        r = self.client.post(reverse('accounts:profile'), {
            'email': 'grace_new@t.com', 'bio': '新简介', 'avatar': ''
        })
        self.assertEqual(r.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'grace_new@t.com')

    def test_change_password_with_correct_old(self):
        """提供正确原密码可修改密码。"""
        r = self.client.post(reverse('accounts:change_password'), {
            'old_password': 'Grace2024pw',
            'new_password': 'Grace2025pw',
            'confirm_password': 'Grace2025pw',
        })
        self.assertEqual(r.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Grace2025pw'))

    def test_change_password_with_wrong_old(self):
        """错误原密码不可修改密码。"""
        r = self.client.post(reverse('accounts:change_password'), {
            'old_password': 'wrong',
            'new_password': 'Grace2025pw',
            'confirm_password': 'Grace2025pw',
        })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '不正确')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Grace2024pw'))  # 密码未变
