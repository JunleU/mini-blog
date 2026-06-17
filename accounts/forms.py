"""用户模块表单。

依据 SRS：
  - UC01 用户注册：用户名 4-20 字符（字母数字下划线）、密码 6-128 含字母与数字、
    邮箱唯一。
  - UC11 管理个人信息：修改密码需验证当前密码；修改邮箱。
"""

import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


# 用户名规则：仅字母、数字、下划线，4-20 字符（SRS UC01）
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{4,20}$')


class UserRegisterForm(forms.ModelForm):
    """用户注册表单（UC01）。

    字段：username / email / password / confirm_password
    """

    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        min_length=6,
        max_length=128,
        help_text='长度 6-128 个字符，必须同时包含字母和数字。',
    )
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }

    # ---- 字段级校验 ----
    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if not USERNAME_PATTERN.match(username):
            raise ValidationError('用户名只能包含字母、数字和下划线，长度 4-20 个字符。')
        if User.objects.filter(username=username).exists():
            raise ValidationError('该用户名已被注册。')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('该邮箱已被注册。')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        # 必须同时包含字母和数字（SRS UC01）
        if not (re.search(r'[A-Za-z]', password) and re.search(r'[0-9]', password)):
            raise ValidationError('密码必须同时包含字母和数字。')
        # 复用 Django 内置强度校验（最小长度、常见密码、纯数字等）
        validate_password(password)
        return password

    # ---- 整表校验 ----
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', '两次输入的密码不一致。')
        return cleaned_data

    def save(self, commit=True):
        """创建用户并对密码做 PBKDF2 哈希加盐（由 Django set_password 完成）。"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # 哈希加盐存储
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """用户登录表单（UC02）。

    登录失败时返回统一的模糊错误信息，防止用户枚举攻击（SRS UC02）。
    """

    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput(attrs={'class': 'form-input', 'autofocus': True}),
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )

    def __init__(self, *args, **kwargs):
        # Django 的 LoginView 会传入 request，这里取出供 clean() 使用
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self._user_cache = None

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            # 先尝试标准认证（Django ModelBackend 会对禁用用户返回 None）
            user = authenticate(
                self.request, username=username, password=password
            )
            if user is not None:
                self._user_cache = user
                cleaned_data['user'] = user
            else:
                # 认证失败：判断是否因账号被禁用（SRS UC02 要求明确提示）。
                # 用 check_password 单独验证，避免因禁用而误报"密码错误"。
                try:
                    candidate = User.objects.get(username=username)
                except User.DoesNotExist:
                    candidate = None
                if candidate is not None and candidate.check_password(password):
                    # 密码正确但 authenticate 返回 None → 账号被禁用
                    raise ValidationError('该账号已被禁用，请联系管理员。')
                # 其余情况（用户不存在或密码错误）统一模糊提示，防枚举
                raise ValidationError('用户名或密码错误。')
        return cleaned_data

    def get_user(self):
        """供 Django LoginView.form_valid() 获取已认证用户。"""
        return self._user_cache


class ProfileForm(forms.ModelForm):
    """个人信息修改表单（UC11）——修改邮箱、简介、头像。"""

    class Meta:
        model = User
        fields = ['email', 'bio', 'avatar']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'avatar': forms.URLInput(
                attrs={'class': 'form-input', 'placeholder': '头像图片 URL（可选）'}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        # 排除当前用户后检查唯一性
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('该邮箱已被注册。')
        return email


class PasswordChangeForm(forms.Form):
    """修改密码表单（UC11）——需验证当前密码。

    不同于 Django 内置 SetPasswordForm，这里显式要求输入原密码。
    """

    old_password = forms.CharField(
        label='当前密码',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )
    new_password = forms.CharField(
        label='新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        min_length=6,
        max_length=128,
        help_text='长度 6-128 个字符，必须同时包含字母和数字。',
    )
    confirm_password = forms.CharField(
        label='确认新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old):
            raise ValidationError('当前密码不正确。')
        return old

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password', '')
        if not (re.search(r'[A-Za-z]', new_password) and re.search(r'[0-9]', new_password)):
            raise ValidationError('新密码必须同时包含字母和数字。')
        validate_password(new_password, user=self.user)
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')
        if new_password and confirm and new_password != confirm:
            self.add_error('confirm_password', '两次输入的新密码不一致。')
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password'])
        self.user.save()
        return self.user
