/* Trang quản trị Tiệm Bánh Ngọt:
   1) nút đổi giao diện sáng / tối (nhớ lựa chọn trong trình duyệt)
   2) nút bấm nhanh gửi yêu cầu POST (đổi trạng thái đơn hàng...)
   3) việt hóa vài chữ tiếng Anh còn sót của giao diện */
(function () {
    "use strict";
    var KEY = "bn-admin-theme";

    /* ---------- 1. Sáng / tối ---------- */
    function saved() {
        try { return localStorage.getItem(KEY) || "light"; } catch (e) { return "light"; }
    }
    function save(mode) {
        try { localStorage.setItem(KEY, mode); } catch (e) {}
    }
    function apply(mode) {
        document.documentElement.setAttribute("data-bs-theme", mode);       // Bootstrap 5.3
        if (document.body) { document.body.classList.toggle("dark-mode", mode === "dark"); }
        var btn = document.getElementById("bn-theme-toggle");
        if (btn) {
            btn.textContent = mode === "dark" ? "☀️" : "🌙";
            btn.title = mode === "dark" ? "Chuyển sang giao diện sáng" : "Chuyển sang giao diện tối";
        }
    }
    apply(saved());   // áp dụng sớm để tránh nháy trắng khi tải trang

    function findNavbarList() {
        var nav = document.querySelector("nav.navbar") || document.querySelector(".main-header, .app-header");
        if (!nav) { return null; }
        var lists = nav.querySelectorAll("ul.navbar-nav");
        return lists.length ? lists[lists.length - 1] : null;   // danh sách cuối = bên phải (menu người dùng)
    }

    function initThemeToggle() {
        if (document.getElementById("bn-theme-toggle")) { return; }
        var btn = document.createElement("a");
        btn.id = "bn-theme-toggle";
        btn.href = "#";
        btn.setAttribute("role", "button");

        var bar = findNavbarList();
        if (bar) {
            btn.className = "nav-link";
            var li = document.createElement("li");
            li.className = "nav-item";
            li.appendChild(btn);
            bar.insertBefore(li, bar.firstChild);
        } else {
            btn.className = "bn-floating";   // không tìm thấy thanh trên -> nút nổi góc phải dưới
            document.body.appendChild(btn);
        }

        btn.addEventListener("click", function (e) {
            e.preventDefault();
            var next = document.documentElement.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
            save(next);
            apply(next);
        });
        apply(saved());
    }

    /* ---------- 2. Nút POST nhanh: <button data-bn-post="url" data-confirm="câu hỏi"> ---------- */
    function getCookie(name) {
        var parts = ("; " + document.cookie).split("; " + name + "=");
        return parts.length === 2 ? decodeURIComponent(parts.pop().split(";").shift()) : "";
    }

    function initPostButtons() {
        document.addEventListener("click", function (e) {
            var btn = e.target.closest ? e.target.closest("[data-bn-post]") : null;
            if (!btn) { return; }
            e.preventDefault();
            var question = btn.getAttribute("data-confirm");
            if (question && !window.confirm(question)) { return; }

            var form = document.createElement("form");
            form.method = "post";
            form.action = btn.getAttribute("data-bn-post");
            var token = document.createElement("input");
            token.type = "hidden";
            token.name = "csrfmiddlewaretoken";
            token.value = getCookie("csrftoken");
            form.appendChild(token);
            document.body.appendChild(form);
            form.submit();
        });
    }

    /* ---------- 3. Việt hóa chữ còn sót (chỉ thay khi khớp nguyên chữ) ---------- */
    var VI = {
        "Dashboard": "Tổng quan",
        "Recent actions": "Hoạt động gần đây",
        "My actions": "Hoạt động của tôi",
        "None available": "Chưa có"
    };

    function translateTexts() {
        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
        var nodes = [], node;
        while ((node = walker.nextNode())) { nodes.push(node); }
        nodes.forEach(function (t) {
            var tag = t.parentNode && t.parentNode.nodeName;
            if (tag === "SCRIPT" || tag === "STYLE" || tag === "TEXTAREA") { return; }
            var text = t.nodeValue.trim();
            if (Object.prototype.hasOwnProperty.call(VI, text)) {
                t.nodeValue = t.nodeValue.replace(text, VI[text]);
            }
        });
    }

    /* Chữ gợi ý trong ô tìm kiếm trên thanh menu: "Tìm kiếm Sản Phẩm..." -> "Tìm sản phẩm…" */
    function tidySearchPlaceholders() {
        var inputs = document.querySelectorAll("nav.navbar form input[placeholder]");
        Array.prototype.forEach.call(inputs, function (input) {
            var m = input.getAttribute("placeholder").match(/^Tìm kiếm\s+(.*?)\.*$/i);
            if (m) { input.setAttribute("placeholder", "Tìm " + m[1].toLowerCase() + "…"); }
        });
    }

    function init() {
        initThemeToggle();
        initPostButtons();
        translateTexts();
        tidySearchPlaceholders();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
