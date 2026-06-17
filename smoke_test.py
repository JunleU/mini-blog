"""端到端冒烟测试：通过 Django 测试客户端验证完整业务流程。

覆盖 SRS 关键用例：
  UC01 注册、UC02 登录、UC03 发表、UC04 修改、UC05 删除、
  UC06 浏览、UC07 评论、UC08-UC10 后台管理、UC11 个人信息。
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miniblog.settings')
os.environ.setdefault('DJANGO_DEBUG', '1')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

c = Client()
passed = 0
failed = 0


def check(name, condition, detail=''):
    global passed, failed
    if condition:
        passed += 1
        print(f'  ✅ {name}')
    else:
        failed += 1
        print(f'  ❌ {name}  {detail}')


print('=' * 60)
print('Mini Blog 端到端冒烟测试')
print('=' * 60)

# ---- UC06 浏览文章（匿名访客） ----
print('\n[UC06] 浏览文章（匿名访客）')
r = c.get('/')
check('首页返回 200', r.status_code == 200, f'实际 {r.status_code}')
check('首页含文章标题', '欢迎来到 Mini Blog' in r.content.decode())
check('首页含分类侧边栏', '技术随笔' in r.content.decode())

# 文章详情页（用实际存在的文章 pk）
from blog.models import Article, Category  # noqa: E402
seed_article = Article.objects.first()
r = c.get(seed_article.get_absolute_url())
check('详情页返回 200', r.status_code == 200, f'实际 {r.status_code}')
check('详情页渲染 Markdown', '<h1>' in r.content.decode() or '<h2>' in r.content.decode())
check('详情页含评论区', '评论' in r.content.decode())

# 404 测试
r = c.get('/article/99999/')
check('不存在文章返回 404', r.status_code == 404, f'实际 {r.status_code}')

# ---- UC01 用户注册 ----
print('\n[UC01] 用户注册')
r = c.get('/accounts/register/')
check('注册页返回 200', r.status_code == 200)

# 成功注册
r = c.post('/accounts/register/', {
    'username': 'newuser',
    'email': 'new@test.com',
    'password': 'Test2024pass',
    'confirm_password': 'Test2024pass',
})
check('注册成功重定向', r.status_code in (302, 301), f'实际 {r.status_code}')
check('新用户已入库', User.objects.filter(username='newuser').exists())

# 重复用户名注册失败
r = c.post('/accounts/register/', {
    'username': 'newuser',
    'email': 'other@test.com',
    'password': 'Test2024pass',
    'confirm_password': 'Test2024pass',
})
check('重复用户名被拒绝', r.status_code == 200 and '已被注册' in r.content.decode())

# 密码不一致
r = c.post('/accounts/register/', {
    'username': 'newuser2',
    'email': 'new2@test.com',
    'password': 'Test2024pass',
    'confirm_password': 'different123',
})
check('密码不一致被拒绝', r.status_code == 200 and '不一致' in r.content.decode())

# 密码无数字
r = c.post('/accounts/register/', {
    'username': 'newuser3',
    'email': 'new3@test.com',
    'password': 'passwordABC',
    'confirm_password': 'passwordABC',
})
check('纯字母密码被拒绝', r.status_code == 200 and '字母和数字' in r.content.decode())

# ---- UC02 用户登录 ----
print('\n[UC02] 用户登录')
r = c.post('/accounts/login/', {'username': 'demo', 'password': 'demo123'})
check('登录成功重定向', r.status_code in (302, 301), f'实际 {r.status_code}')

# 验证登录状态：能访问发表文章页
r = c.get('/article/new/')
check('登录后可访问发文页', r.status_code == 200, f'实际 {r.status_code}')

# 错误密码登录
c2 = Client()
r = c2.post('/accounts/login/', {'username': 'demo', 'password': 'wrong'})
check('错误密码登录失败', r.status_code == 200 and '用户名或密码错误' in r.content.decode())

# ---- UC03 发表文章 ----
print('\n[UC03] 发表文章')
r = c.post('/article/new/', {
    'title': '我的测试文章',
    'content': '## 这是测试内容\n\n含 **加粗** 和 `代码`。',
    'category': '',
    'status': 'published',
})
check('发表文章重定向到详情', r.status_code in (302, 301), f'实际 {r.status_code}')

# 找到新文章
new_article = Article.objects.filter(title='我的测试文章').first()
check('文章已入库', new_article is not None)
if new_article:
    r = c.get(new_article.get_absolute_url())
    check('新文章详情可访问', r.status_code == 200)
    check('Markdown 加粗已渲染', '<strong>加粗</strong>' in r.content.decode())

# 标题为空被拒
r = c.post('/article/new/', {
    'title': '',
    'content': '内容',
    'status': 'published',
})
check('空标题被拒', r.status_code == 200 and ('不能为空' in r.content.decode() or '必填项' in r.content.decode()))

# ---- UC04 修改文章 ----
print('\n[UC04] 修改文章')
if new_article:
    r = c.post(f'/article/{new_article.pk}/edit/', {
        'title': '我的测试文章（已修改）',
        'content': '修改后的内容',
        'category': '',
        'status': 'published',
    })
    check('修改文章重定向', r.status_code in (302, 301), f'实际 {r.status_code}')
    new_article.refresh_from_db()
    check('标题已更新', '已修改' in new_article.title)

# 非作者不能修改（用 newuser 登录后尝试改 demo 的文章）
c3 = Client()
c3.post('/accounts/login/', {'username': 'newuser', 'password': 'Test2024pass'})
if new_article:
    r = c3.post(f'/article/{new_article.pk}/edit/', {
        'title': '恶意修改',
        'content': 'x',
        'status': 'published',
    })
    check('非作者修改被拒(403)', r.status_code == 403, f'实际 {r.status_code}')

# ---- UC07 发表评论 ----
print('\n[UC07] 发表评论')
if new_article:
    r = c.post(f'/comments/{new_article.pk}/create/', {'content': '一条测试评论'})
    check('评论发表重定向', r.status_code in (302, 301), f'实际 {r.status_code}')
    from comments.models import Comment
    check('评论已入库', Comment.objects.filter(article=new_article, content='一条测试评论').exists())

    # 空评论被拒
    r = c.post(f'/comments/{new_article.pk}/create/', {'content': ''})
    check('空评论被拒', r.status_code in (302, 301))

    # XSS 测试：评论中的 script 标签应被剥离
    r = c.post(f'/comments/{new_article.pk}/create/', {
        'content': '<script>alert(1)</script>正常文字'
    })
    r = c.get(new_article.get_absolute_url())
    check('XSS script 被过滤', '<script>' not in r.content.decode(), 'script 标签未被过滤！')

# 未登录不能评论
c4 = Client()
if new_article:
    r = c4.post(f'/comments/{new_article.pk}/create/', {'content': '匿名评论'})
    check('未登录评论被拒(302到登录)', r.status_code in (302, 301))

# ---- UC05 删除文章 ----
print('\n[UC05] 删除文章')
if new_article:
    pk = new_article.pk
    r = c.post(f'/article/{pk}/delete/')
    check('删除文章重定向', r.status_code in (302, 301), f'实际 {r.status_code}')
    check('文章已删除', not Article.objects.filter(pk=pk).exists())
    check('关联评论级联删除',
          not Comment.objects.filter(article_id=pk).exists())

# ---- UC11 个人信息 ----
print('\n[UC11] 管理个人信息')
r = c.get('/accounts/profile/')
check('个人中心可访问', r.status_code == 200)
r = c.post('/accounts/profile/', {
    'email': 'demo_updated@test.com',
    'bio': '更新的简介',
    'avatar': '',
})
check('资料更新成功', r.status_code in (302, 301))
u = User.objects.get(username='demo')
check('邮箱已更新', u.email == 'demo_updated@test.com')

# 修改密码
r = c.post('/accounts/password/', {
    'old_password': 'demo123',
    'new_password': 'newpass123',
    'confirm_password': 'newpass123',
})
check('密码修改成功', r.status_code in (302, 301))

# 错误原密码
r = c.post('/accounts/password/', {
    'old_password': 'wrong',
    'new_password': 'another123',
    'confirm_password': 'another123',
})
check('错误原密码被拒', r.status_code == 200 and '不正确' in r.content.decode())

# ---- UC08-UC10 后台管理 ----
print('\n[UC08-UC10] 后台管理')
# 普通用户不能访问后台
r = c3.get('/manage/')
check('普通用户访问后台被拒(403)', r.status_code == 403, f'实际 {r.status_code}')

# 管理员登录
c_admin = Client()
c_admin.post('/accounts/login/', {'username': 'admin', 'password': 'admin123'})

r = c_admin.get('/manage/')
check('管理员仪表盘 200', r.status_code == 200, f'实际 {r.status_code}')
check('仪表盘含统计', '注册用户' in r.content.decode() or 'user_count' in r.content.decode())

# 用户管理
r = c_admin.get('/manage/users/')
check('用户列表 200', r.status_code == 200)
check('用户列表含数据', 'demo' in r.content.decode())

# 文章管理
r = c_admin.get('/manage/articles/')
check('文章列表 200', r.status_code == 200)

# 评论管理
r = c_admin.get('/manage/comments/')
check('评论列表 200', r.status_code == 200)

# 搜索功能
r = c_admin.get('/manage/users/?q=demo')
check('用户搜索 200', r.status_code == 200)

# ---- CSRF 防护测试 ----
print('\n[安全] CSRF 防护')
c5 = Client(enforce_csrf_checks=True)
r = c5.post('/accounts/login/', {'username': 'demo', 'password': 'newpass123'})
check('无 CSRF token 请求被拒(403)', r.status_code == 403, f'实际 {r.status_code}')

# ---- 汇总 ----
print('\n' + '=' * 60)
print(f'测试结果：✅ {passed} 通过  ❌ {failed} 失败')
print('=' * 60)
exit(0 if failed == 0 else 1)
