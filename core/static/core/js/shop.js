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
        document.querySelectorAll(".theme-toggle").forEach(function (btn) {
            var label = btn.getAttribute("data-label");
            btn.textContent = (theme === "dark" ? "☀️" : "🌙") + (label ? "  " + (theme === "dark" ? "Giao diện sáng" : "Giao diện tối") : "");
            btn.title = theme === "dark" ? "Chuyển sang giao diện sáng" : "Chuyển sang giao diện tối";
            btn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
        });
    }

    function initTheme() {
        var saved = stored();
        applyTheme(saved === "dark" || saved === "light" ? saved : currentTheme());
        document.querySelectorAll(".theme-toggle").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var next = currentTheme() === "dark" ? "light" : "dark";
                remember(next);
                applyTheme(next);
            });
        });
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

    /* ---------- Ô tìm kiếm trượt xuống từ biểu tượng 🔍 ---------- */
    function initSearch() {
        var toggle = document.querySelector(".search-toggle");
        var panel = document.getElementById("search-panel");
        if (!toggle || !panel) { return; }
        function setOpen(open) {
            panel.hidden = !open;
            toggle.setAttribute("aria-expanded", open ? "true" : "false");
            if (open) {
                var input = panel.querySelector("input[type=text]");
                if (input) { input.focus(); }
            }
        }
        toggle.addEventListener("click", function () { setOpen(panel.hidden); });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && !panel.hidden) { setOpen(false); }
        });
        /* đang tìm dở (có từ khóa) thì mở sẵn ô tìm kiếm */
        var input = panel.querySelector("input[type=text]");
        if (input && input.value) { setOpen(true); }
    }

    /* ---------- Nút ↑ lên đầu trang ---------- */
    function initToTop() {
        var btn = document.querySelector(".float-top");
        if (!btn) { return; }
        function update() { btn.hidden = window.scrollY < 400; }
        window.addEventListener("scroll", update, { passive: true });
        btn.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
        update();
    }

    /* ---------- Nút − / + cạnh ô số lượng ---------- */
    function initQty() {
        document.querySelectorAll(".qty-stepper").forEach(function (box) {
            var input = box.querySelector("input");
            if (!input) { return; }
            box.querySelectorAll("[data-step]").forEach(function (btn) {
                btn.addEventListener("click", function () {
                    var step = parseInt(btn.getAttribute("data-step"), 10) || 0;
                    var min = parseInt(input.min, 10) || 1;
                    var max = parseInt(input.max, 10) || 9999;
                    var value = (parseInt(input.value, 10) || min) + step;
                    input.value = Math.min(Math.max(value, min), max);
                });
            });
        });
    }

    /* ---------- Ảnh bánh bị hỏng / mất file -> hiện biểu tượng 🍰 thay vì chữ thay thế ---------- */
    function initBrokenImages() {
        function fallback(img) {
            var span = document.createElement("span");
            span.textContent = "🍰";
            span.setAttribute("role", "img");
            span.setAttribute("aria-label", img.alt || "Bánh");
            img.replaceWith(span);
        }
        document.querySelectorAll(".thumb img, .detail-image img, .mini-thumb img, .news-thumb img").forEach(function (img) {
            if (img.complete && img.naturalWidth === 0) { fallback(img); }
            else { img.addEventListener("error", function () { fallback(img); }, { once: true }); }
        });
    }

    function init() {
        initBrokenImages();
        initTheme();
        initMenu();
        initSearch();
        initToTop();
        initQty();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
