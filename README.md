# Mini Blog · 博客网站系统

> 软件工程与实践课程项目 · 基于 Django + MySQL 的 B/S 架构轻量级博客平台

## 项目简介

Mini Blog 是一个采用 B/S 架构的轻量级博客网站系统，支持注册用户发表与管理文章、
用户间评论互动，以及管理员的后台数据管理。系统依据完整的软件工程规范开发，
配套有《可行性分析报告（FAR）》《软件需求规格说明（SRS）》《体系结构设计文档（SAD）》
三份文档（见 `doc/` 目录）。

## 技术栈

| 层次 | 技术选型 | 说明 |
|------|----------|------|
| 表示层 | HTML5 / CSS3 / JavaScript | 原生技术，无重型前端框架，响应式设计 |
| 业务逻辑层 | Python 3.10+ / Django 4.2 | MTV 模式，ORM、Auth、Session 内置 |
| 数据持久层 | MySQL 8.0（生产）/ SQLite（开发） | 通过 Django ORM 访问，可切换 |

**运行环境**：Linux / Windows / macOS 均可，需 Python 3.10+ 。

## 功能模块

系统划分为四个核心模块，覆盖课程课题全部要求：

| 模块 | Django App | 覆盖用例 | 说明 |
|------|-----------|----------|------|
| 用户模块 | `accounts` | UC01/UC02/UC11 | 注册、登录、登出、个人信息与密码管理 |
| 博客模块 | `blog` | UC03-UC06 | 文章发表、修改、删除、列表、详情、分类 |
| 评论模块 | `comments` | UC07 | 评论提交、展示、删除 |
| 后台管理 | `admin_panel` | UC08-UC10 | 管理员对用户/文章/评论的查询、修改、删除 |

## 目录结构

```
mini-blog/
├── doc/                    # 项目文档
│   ├── 课题.md
│   ├── FAR.pdf
│   ├── SRS.pdf
│   └── SAD.pdf
├── miniblog/               # 项目配置（settings / urls / wsgi）
├── accounts/               # M01 用户模块
├── blog/                   # M02 博客模块
├── comments/               # M03 评论模块
├── admin_panel/            # M04 后台管理模块
├── templates/              # 全局模板（base.html / 错误页 / 各模块页面）
├── static/                 # 静态资源（CSS / JS）
├── manage.py               # Django 管理脚本
├── requirements.txt        # Python 依赖
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境（Python 3.10+）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

默认使用 **SQLite**（零配置，适合本地开发与演示）。切换至 MySQL：

```bash
# 通过环境变量启用 MySQL 后端
export DJANGO_DB_ENGINE=mysql
export DJANGO_DB_NAME=miniblog_db
export DJANGO_DB_USER=miniblog
export DJANGO_DB_PASSWORD=你的密码
export DJANGO_DB_HOST=127.0.0.1
export DJANGO_DB_PORT=3306
```

### 3. 初始化与运行

```bash
# 生成并应用数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建初始数据（分类、管理员、示例用户、示例文章）
python manage.py seed

# 启动开发服务器
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 即可使用。

### 4. 测试账号

`seed` 命令会创建以下账号：

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | `admin` | `admin123` | 可访问 `/manage/` 后台与 `/dj-admin/` |
| 普通用户 | `demo` | `demo123` | 已发表示例文章 |

## 使用指南

### 普通用户

- **浏览**：访问首页查看文章列表，点击标题阅读全文（无需登录）
- **注册/登录**：点击右上角"注册"/"登录"
- **发表文章**：登录后点击"写文章"，支持 Markdown 语法
- **评论**：在文章详情页底部发表评论
- **管理文章**：在自己的文章详情页点击"编辑"/"删除"
- **个人信息**：点击"个人中心"修改邮箱、简介、头像或密码

### 管理员

- 登录后导航栏出现"后台管理"入口（`/manage/`）
- **仪表盘**：查看全站数据统计
- **用户管理**：搜索、编辑角色、启用/禁用、删除用户
- **文章管理**：搜索、编辑、删除任意文章
- **评论管理**：搜索、删除任意评论
- 另可通过 `/dj-admin/` 访问 Django 内置 admin

## 测试

项目包含 54 个 Django 单元测试，覆盖全部用例与安全防护：

```bash
# 运行全部测试
python manage.py test

# 运行指定模块测试
python manage.py test accounts blog
```

测试覆盖：
- **accounts**（17 项）：注册校验、登录认证、密码修改、个人信息
- **blog**（20 项）：文章 CRUD、权限控制、Markdown 渲染、分类
- **comments**（8 项）：评论提交、XSS 过滤、级联删除、权限
- **admin_panel**（9 项）：后台权限、用户/文章/评论管理

另提供端到端冒烟测试脚本 `smoke_test.py`（需先 `seed`）：

```bash
python smoke_test.py
```

## 安全设计

系统落实 SRS §3.10 与 SAD §3.3 的安全需求：

- **密码安全**：PBKDF2 + SHA256 哈希加盐存储（Django 默认），不存明文
- **CSRF 防护**：Django CSRF 中间件验证所有 POST 请求的 Token
- **XSS 防护**：文章 Markdown 经 bleach 过滤危险标签；评论剥离所有 HTML；模板自动转义
- **SQL 注入防护**：全程使用 Django ORM 参数化查询，无原始 SQL 拼接
- **会话安全**：Session Cookie 设 HttpOnly、SameSite=Lax，30 分钟超时
- **权限控制**：登录认证 + 作者所有权校验 + 管理员角色校验三层防护
- **防用户枚举**：登录失败返回统一的"用户名或密码错误"模糊提示
- **错误页面**：自定义 403 / 404 / 500 / CSRF 失败页面，生产环境关闭 DEBUG

## 部署（生产环境）

```bash
# 1. 关闭 DEBUG，配置环境变量
export DJANGO_DEBUG=0
export DJANGO_SECRET_KEY='你的随机密钥'
export DJANGO_ALLOWED_HOSTS='yourdomain.com'
export DJANGO_DB_ENGINE=mysql
# ...其余 MySQL 环境变量

# 2. 收集静态文件
python manage.py collectstatic --noinput

# 3. 用 Gunicorn 运行
pip install gunicorn
gunicorn miniblog.wsgi:application --bind 127.0.0.1:8000 --workers 3

# 4. Nginx 反向代理指向 Gunicorn（配置示例见 SAD §5）
```

## 与文档的差异说明

实际实现与 FAR/SRS/SAD 文档规划基本一致，少量调整如下：

1. **数据库**：开发环境默认 SQLite（便于零配置启动），通过环境变量切换 MySQL，
   对应 SAD §3.2 的 MySQL 规划。
2. **头像字段**：因环境未安装 Pillow，`User.avatar` 采用 `URLField`（存头像 URL）
   替代 `ImageField`，功能等价。
3. **后台管理**：`admin_panel` 模块为面向管理员角色的独立管理界面
   （对应 SRS UC08-UC10），同时保留 Django 内置 admin（路径改为 `/dj-admin/`）
   作为补充手段。
4. **文章正文**：支持 Markdown 语法（SRS UC03），渲染时用 bleach 做 XSS 过滤。
5. **虚拟环境**: 可不使用 conda ，选用更轻量的 Python 内置模块 venv

## 项目文档

详细的需求与设计文档位于 `doc/` 目录：

- `FAR.pdf` —— 可行性分析报告
- `SRS.pdf` —— 软件需求规格说明
- `SAD.pdf` —— 体系结构设计文档

---

© 2026 软件工程与实践课程项目 · 刘俊汝
