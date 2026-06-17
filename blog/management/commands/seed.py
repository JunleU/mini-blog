"""seed 管理命令：创建初始分类与示例数据，便于演示与验收。

用法：
    python manage.py seed           # 创建分类 + 演示用户/文章
    python manage.py seed --reset   # 清空后重建（仅开发环境）

依据 SRS §3.15 操作：初始化操作需导入初始分类数据。
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from blog.models import Article, Category
from comments.models import Comment

User = get_user_model()

CATEGORIES = [
    ('技术随笔', '编程技术、开发心得相关文章'),
    ('课程笔记', '课程学习笔记与总结'),
    ('生活感悟', '日常生活与个人感悟'),
    ('项目实践', '软件项目实践记录'),
]

SAMPLE_ARTICLE = """# 欢迎来到 Mini Blog

这是一个基于 **Django** 框架构建的轻量级博客系统。

## 主要功能

- 用户注册与登录
- 文章的发表、修改、删除
- 文章分类与搜索
- 评论互动
- 管理员后台管理

## 技术栈

| 层次 | 技术 |
|------|------|
| 表示层 | HTML5 / CSS3 / JavaScript |
| 业务层 | Python Django 4.2 |
| 数据层 | MySQL 8.0 / SQLite |

### 代码示例

```python
def hello():
    print("Hello, Mini Blog!")
```

> 本系统为软件工程与实践课程项目，采用 B/S 架构设计。

Enjoy writing! 🎉
"""


class Command(BaseCommand):
    help = '创建初始分类与示例数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='清空所有数据后重建（仅开发环境使用）',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        if reset:
            Comment.objects.all().delete()
            Article.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING('已清空现有数据。'))

        # 1. 创建分类
        cats = {}
        for name, desc in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=name, defaults={'description': desc}
            )
            cats[name] = cat
            if created:
                self.stdout.write(f'  创建分类：{name}')

        # 2. 创建管理员账号（如不存在）
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@miniblog.local',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'bio': '系统管理员',
            },
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(
                '  创建管理员：admin / admin123'
            ))
        else:
            self.stdout.write('  管理员 admin 已存在，跳过。')

        # 3. 创建示例作者
        author, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@miniblog.local',
                'role': User.Role.AUTHOR,
                'bio': '一位热爱写作的博主',
            },
        )
        if created:
            author.set_password('demo123')
            author.save()
            self.stdout.write(self.style.SUCCESS(
                '  创建示例用户：demo / demo123'
            ))
        else:
            self.stdout.write('  示例用户 demo 已存在，跳过。')

        # 4. 创建示例文章（如不存在）
        if not Article.objects.filter(title='欢迎来到 Mini Blog').exists():
            article = Article.objects.create(
                title='欢迎来到 Mini Blog',
                content=SAMPLE_ARTICLE,
                author=author,
                category=cats['项目实践'],
                status=Article.Status.PUBLISHED,
            )
            # 添加一条示例评论
            Comment.objects.create(
                content='第一篇博文，支持一下！',
                author=author,
                article=article,
            )
            self.stdout.write(self.style.SUCCESS('  创建示例文章与评论。'))

        self.stdout.write(self.style.SUCCESS('\n✅ 初始化完成！'))
        self.stdout.write('  管理员：admin / admin123')
        self.stdout.write('  示例用户：demo / demo123')
        self.stdout.write('  访问 http://127.0.0.1:8000/ 开始使用')
