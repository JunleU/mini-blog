"""Markdown 渲染与 XSS 过滤工具。

依据 SRS §3.10：用户输入内容存储前过滤 HTML 标签，渲染时自动转义。
文章正文支持 Markdown，渲染为 HTML 后用 bleach 过滤危险标签与属性。
"""

import bleach
import markdown as md

# Markdown 扩展：extra 含表格/脚注等；codehilite 代码高亮；fenced_code 围栏代码块
MD_EXTENSIONS = ['extra', 'nl2br', 'sane_lists']

# 允许的 HTML 标签白名单（bleach 过滤后只保留这些）
ALLOWED_TAGS = [
    'p', 'br', 'hr', 'span', 'div',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'b', 'em', 'i', 'u', 's', 'del', 'sub', 'sup', 'mark',
    'blockquote', 'code', 'pre', 'kbd',
    'ul', 'ol', 'li', 'dl', 'dt', 'dd',
    'a', 'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
]

# 允许的属性白名单
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'span': ['class'],
    'div': ['class'],
    'code': ['class'],
    'th': ['align'],
    'td': ['align'],
}

# 允许的 CSS 协议/样式（这里不放开 style 属性，仅允许 class）


def render_markdown(text):
    """将 Markdown 文本渲染为经过 XSS 过滤的安全 HTML。

    流程：Markdown → HTML → bleach.clean（剥离 script/事件处理器等）。
    """
    if not text:
        return ''
    html = md.markdown(text, extensions=MD_EXTENSIONS, output_format='html5')
    safe_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=['http', 'https', 'mailto'],
        strip=True,
    )
    return safe_html


def plain_text(text, length=150):
    """将 Markdown 转为纯文本摘要。"""
    if not text:
        return ''
    import re
    plain = re.sub(r'[#*`>\-_~\[\]\(\)!]', '', text)
    plain = re.sub(r'\s+', ' ', plain).strip()
    return plain[:length] + ('…' if len(plain) > length else '')
