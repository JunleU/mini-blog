"""后台管理模块表单（M04）。

供管理员在后台修改用户角色/状态、修改文章等使用。
"""

from django import forms

from accounts.models import User
from blog.models import Article


class UserAdminForm(forms.ModelForm):
    """管理员修改用户表单（UC08）——可调整角色与启用状态。"""

    class Meta:
        model = User
        fields = ['role', 'is_active', 'email', 'bio']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class ArticleAdminForm(forms.ModelForm):
    """管理员修改文章表单（UC09）——可调整状态、标题、正文、分类。"""

    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 12}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }
