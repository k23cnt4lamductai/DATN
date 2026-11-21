/* Trang bán hàng: nút đổi sáng / tối (nhớ lựa chọn) và menu ☰ trên điện thoại */
(function () {
    "use strict";
    var KEY = "bn-shop-theme";
    var MOBILE_MAX = 980;

    /* ---------- Sáng / tối ---------- */
    function stored() {
        try { return localStorage.getItem(KEY); } catch (e) { return null; }
    }
    function remember(theme) {
        try { localStorage.setItem(KEY, theme); } catch (e) {}
    }
    function currentTheme() {
        return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    }
    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        var btn = document.getElementById("shop-theme-toggle");
        if (btn) {
            btn.textContent = theme === "dark" ? "☀️" : "🌙";
            btn.title = theme === "dark" ? "Chuyển sang giao diện sáng" : "Chuyển sang giao diện tối";
            btn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
        }
    }

    function initTheme() {
        var saved = stored();
        applyTheme(saved === "dark" || saved === "light" ? saved : currentTheme());
        var btn = document.getElementById("shop-theme-toggle");
        if (btn) {
            btn.addEventListener("click", function () {
                var next = currentTheme() === "dark" ? "light" : "dark";
                remember(next);
                applyTheme(next);
            });
        }
    }

    /* ---------- Menu ☰ trên điện thoại ---------- */
    function initMenu() {
        var toggle = document.querySelector(".menu-toggle");
        var panel = document.getElementById("mobile-panel");
        if (!toggle || !panel) { return; }

        function setOpen(open) {
            panel.hidden = !open;
            toggle.setAttribute("aria-expanded", open ? "true" : "false");
            toggle.setAttribute("aria-label", open ? "Đóng menu" : "Mở menu");
            toggle.textContent = open ? "✕" : "☰";
        }

        toggle.addEventListener("click", function () { setOpen(panel.hidden); });
        panel.addEventListener("click", function (e) {
            if (e.target && e.target.closest && e.target.closest("a")) { setOpen(false); }
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && !panel.hidden) { setOpen(false); }
        });
        window.addEventListener("resize", function () {
            if (window.innerWidth > MOBILE_MAX && !panel.hidden) { setOpen(false); }
        });
    }

    function init() {
        initTheme();
        initMenu();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
