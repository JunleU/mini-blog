"""Mini Blog 项目根 URL 路由。

路由组织（参见 SAD §4.1.1 模块划分）：
  - /                  → blog（博客首页）
  - /accounts/         → accounts（用户认证）
  - /comments/         → comments（评论）
  - /manage/           → admin_panel（后台管理）
  - /dj-admin/         → Django 内置 admin（改用非默认路径，SRS §3.9 安全要求）
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin as dj_admin
from django.urls import include, path

urlpatterns = [
    # 博客模块（首页，根路径）
    path('', include('blog.urls')),
    # 用户模块
    path('accounts/', include('accounts.urls')),
    # 评论模块
    path('comments/', include('comments.urls')),
    # 后台管理模块（面向管理员角色的独立界面）
    path('manage/', include('admin_panel.urls')),
    # Django 内置 admin —— 改用非默认路径 dj-admin（SRS §3.9 安全要求）
    path('dj-admin/', dj_admin.site.urls),
]

# 开发阶段服务用户上传的媒体文件（生产环境由 Nginx 直接服务）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
