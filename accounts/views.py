"""用户模块视图（M01）。

实现 SRS 用例：
  - UC01 用户注册（register）
  - UC02 用户登录（login）
  - 用户登出（logout）
  - UC11 管理个人信息（profile + change_password）
"""

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import (
    PasswordChangeForm,
    ProfileForm,
    UserLoginForm,
    UserRegisterForm,
)


def register(request):
    """UC01 用户注册。

    GET  → 渲染空注册表单。
    POST → 校验数据，通过则创建用户（密码哈希加盐），重定向到登录页。
    失败则回显错误并保留已填合法字段（Django Form 默认行为）。
    """
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'注册成功，欢迎加入 Mini Blog，{user.username}！请登录。')
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


class UserLoginView(LoginView):
    """UC02 用户登录。

    复用 Django LoginView 的认证与跳转逻辑，仅替换表单与模板，
    以满足 SRS 中"用户名或密码错误"的模糊提示要求。
    """

    authentication_form = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('blog:index')

    def form_invalid(self, form):
        # 登录失败时给出统一模糊提示（UserLoginForm 内已校验）
        messages.error(self.request, '用户名或密码错误。')
        return super().form_invalid(form)

    def get_success_url(self):
        # 登录后跳转：管理员进入后台，普通用户进入首页（个人博客入口）
        if self.request.user.is_admin_role:
            return reverse_lazy('admin_panel:dashboard')
        return super().get_success_url()


def logout_view(request):
    """用户登出。使用 POST 以符合 CSRF 安全要求。"""
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, '您已成功退出登录。')
    return redirect('blog:index')


@login_required
def profile(request):
    """UC11 管理个人信息 —— 修改邮箱/简介/头像。"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息已更新。')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password(request):
    """UC11 管理个人信息 —— 修改密码（需验证当前密码）。"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # 修改密码后更新会话哈希，避免用户被登出
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, '密码修改成功。')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
