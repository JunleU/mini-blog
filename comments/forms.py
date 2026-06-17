"""评论模块表单。

依据 SRS UC07：评论内容 1-2000 字符，提交前进行 XSS 过滤。
"""

import bleach

from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    """评论提交表单（UC07）。"""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'class': 'form-input',
                    'rows': 3,
                    'placeholder': '说点什么吧……（1-2000 字符）',
                }
            ),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError('评论内容不能为空。')
        if len(content) > 2000:
            raise forms.ValidationError('评论内容不能超过 2000 个字符。')
        # XSS 过滤：剥离所有 HTML 标签（评论以纯文本展示）
        content = bleach.clean(content, tags=[], strip=True)
        return content
