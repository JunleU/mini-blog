/* Mini Blog 前端交互脚本（原生 JS，无框架依赖） */

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // ---- 删除操作确认（通过 data-confirm 属性触发） ----
    document.body.addEventListener('click', function (e) {
        var target = e.target.closest('[data-confirm]');
        if (!target) return;
        var msg = target.getAttribute('data-confirm');
        if (!confirm(msg)) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }, true);

    // ---- 渐隐消息提示 ----
    document.querySelectorAll('.msg').forEach(function (el) {
        setTimeout(function () {
            el.style.transition = 'opacity 0.5s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 500);
        }, 4000);
    });

    // ---- 表单字段错误高亮 ----
    document.querySelectorAll('.field-error').forEach(function (err) {
        var group = err.closest('.form-group');
        if (group) {
            var input = group.querySelector('input, textarea, select');
            if (input) input.classList.add('invalid');
        }
    });

    // ---- 当前导航高亮（根据 URL 路径匹配）----
    var path = window.location.pathname;
    document.querySelectorAll('.navbar-nav a').forEach(function (a) {
        var href = a.getAttribute('href');
        if (href && (href === path || (href !== '/' && path.indexOf(href) === 0))) {
            a.classList.add('active');
        } else if (href === '/' && path === '/') {
            a.classList.add('active');
        }
    });
});
