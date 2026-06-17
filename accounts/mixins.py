"""通用权限混入类。

提供 AdminRequired（仅管理员）与 AuthorOwnerRequired（仅作者本人）
两类访问控制，供 blog / comments / admin_panel 各视图复用。

依据：SRS §3.10 授权机制；SAD §3.3 安全设计决策。
"""

from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin):
    """要求当前用户为管理员角色（role=admin）。

    未登录 → 重定向到登录页（LoginRequiredMixin 行为）；
    已登录但非管理员 → 抛出 403 PermissionDenied。
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()
        if not getattr(user, 'is_admin_role', False):
            raise PermissionDenied('您没有权限执行此操作。')
        return super().dispatch(request, *args, **kwargs)


class OwnerOrAdminRequiredMixin(LoginRequiredMixin):
    """要求当前用户为对象所有者或管理员。

    子类需实现 get_object() 返回受保护对象，且对象需具有 author 属性。
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()
        obj = self.get_object()
        author = getattr(obj, 'author', None)
        if author != user and not getattr(user, 'is_admin_role', False):
            raise PermissionDenied('您没有权限执行此操作。')
        return super().dispatch(request, *args, **kwargs)
