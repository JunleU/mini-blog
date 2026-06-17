"""博客模块表单。

依据 SRS：
  - UC03 发表文章：标题 1-200 字符，正文 1-50000 字符，分类可选。
  - UC04 修改文章：字段预填充。
"""

from django import forms

from .models import Article, Category


class ArticleForm(forms.ModelForm):
    """文章发表/修改表单（UC03 / UC04）。

    正文使用 textarea，前端可配合 Markdown 编辑器；分类为下拉选择。
    """

    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'status']
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-input', 'placeholder': '请输入文章标题（1-200 字符）'}
            ),
            'content': forms.Textarea(
                attrs={
                    'class': 'form-input markdown-editor',
                    'rows': 18,
                    'placeholder': '支持 Markdown 语法……',
                }
            ),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 分类下拉允许为空（显示"不选择分类"）
        self.fields['category'].required = False
        self.fields['category'].empty_label = '不选择分类'

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('标题不能为空。')
        if len(title) > 200:
            raise forms.ValidationError('标题不能超过 200 个字符。')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        if not content.strip():
            raise forms.ValidationError('文章内容不能为空。')
        if len(content) > 50000:
            raise forms.ValidationError('文章内容不能超过 50000 个字符。')
        return content
