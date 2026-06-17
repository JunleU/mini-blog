"""
Django settings for miniblog project.

Mini Blog 博客网站系统 —— 软件工程与实践课程项目

配置依据：
  - 《可行性分析报告（FAR）》V1.0
  - 《软件需求规格说明（SRS）》V1.0
  - 《体系结构设计文档（SAD）》V1.0

体系结构风格：B/S 架构 + 三层结构（表示层 / 业务逻辑层 / 数据持久层）+ Django MTV 模式。
"""

import os
from pathlib import Path

# 项目根目录：BASE_DIR / 'subdir' 形式构造内部路径
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# 安全配置（参见 SRS §3.10 保密性与私密性需求 / SAD §3.3 安全设计决策）
# =============================================================================
# 生产环境应通过环境变量注入密钥；开发态使用内置默认值便于快速启动。
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-km5qvx0p##008=!@#z8*q1jdab2d#fh^j)&h*lrx1^yzjh64m@',
)

# DEBUG 默认关闭；仅当显式设置 DJANGO_DEBUG=1 时开启（生产环境必须关闭）
DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'

# 允许访问的主机；生产部署时应配置为实际域名/IP
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')


# =============================================================================
# 应用注册（INSTALLED_APPS）
# =============================================================================
# 自定义应用需在 Django 内置应用之前注册，以便自定义 Model/User 生效。
INSTALLED_APPS = [
    # ---- 自定义应用（按 SAD §4.1.1 模块划分）----
    'accounts',       # M01 用户模块：注册、登录、个人信息
    'blog',           # M02 博客模块：文章 CRUD、分类
    'comments',       # M03 评论模块：评论提交/展示/删除
    'admin_panel',    # M04 管理模块：后台管理（独立于 Django Admin）

    # ---- Django 内置应用 ----
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',          # CSRF 防护（SRS §3.10）
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 点击劫持防护
]

ROOT_URLCONF = 'miniblog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 全局模板目录：放置 base.html、错误页面等公共模板
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'miniblog.wsgi.application'


# =============================================================================
# 数据库配置（参见 SAD §3.2 技术选型 / SRS §3.7 软件接口 IF-S02）
# =============================================================================
# 默认使用 SQLite（零配置，便于课程演示与本地开发）。
# 当设置了 DJANGO_DB_ENGINE=mysql 时，切换至 MySQL 8.0（生产/验收部署）。
# 这样既满足 SAD 中 MySQL 的规划，又兼顾本机无 MySQL 的开发场景。
if os.environ.get('DJANGO_DB_ENGINE') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DJANGO_DB_NAME', 'miniblog_db'),
            'USER': os.environ.get('DJANGO_DB_USER', 'miniblog'),
            'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', ''),
            'HOST': os.environ.get('DJANGO_DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('DJANGO_DB_PORT', '3306'),
            # utf8mb4：完整支持 Unicode（含 emoji），参见 SRS IF-S02
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# =============================================================================
# 密码验证（参见 SRS §3.4.1 UC01：密码必须包含字母和数字，6-128 字符）
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},  # SRS UC01：最少 6 个字符
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =============================================================================
# 自定义用户模型（参见 SAD §4.2.4 User：扩展 AbstractUser，新增 role/bio/avatar）
# =============================================================================
# 必须在首次 migrate 之前设置，使自定义 User 模型生效。
AUTH_USER_MODEL = 'accounts.User'


# =============================================================================
# 认证与登录重定向（参见 SRS §3.10 / SAD §3.3）
# =============================================================================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# 会话安全（SRS §3.10：默认 30 分钟无操作自动登出）
SESSION_COOKIE_AGE = 30 * 60          # 1800 秒 = 30 分钟
SESSION_COOKIE_HTTPONLY = True        # 禁止 JS 读取 Session Cookie
SESSION_COOKIE_SAMESITE = 'Lax'       # 缓解 CSRF
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF Cookie 安全
CSRF_COOKIE_HTTPONLY = False          # 需要前端 JS 读取 token（Ajax 提交）
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG        # 生产（HTTPS）下标记 Secure

# Session/CSRF Cookie 在 HTTPS 下标记 Secure
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG and os.environ.get('DJANGO_SSL_REDIRECT', '0') == '1'


# =============================================================================
# 错误页面与 CSRF 失败处理（SRS §3.16 故障处理）
# =============================================================================
CSRF_FAILURE_TEMPLATE = '403_csrf.html'


# =============================================================================
# 安全响应头（SAD §3.3 安全设计决策）
# =============================================================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'  # 禁止被嵌入 iframe，缓解点击劫持


# =============================================================================
# 国际化（中文界面 + 亚洲/上海时区）
# =============================================================================
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True


# =============================================================================
# 静态文件（CSS / JS / 图片）（参见 SAD §4.5 部署）
# =============================================================================
STATIC_URL = '/static/'
# 开发阶段静态文件收集目录；collectstatic 时使用
STATIC_ROOT = BASE_DIR / 'staticfiles'
# 各 App 额外的静态文件查找目录
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 媒体文件（用户上传：头像等）
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================================
# 分页（参见 SRS §3.4.6 UC06：列表页每页 10 条；§3.3 评论每页 10 条）
# =============================================================================
ARTICLES_PER_PAGE = 10
COMMENTS_PER_PAGE = 10
ADMIN_PER_PAGE = 15   # 后台管理列表每页条数


# =============================================================================
# 默认主键字段类型
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
