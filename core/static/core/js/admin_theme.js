/* Nút đổi giao diện sáng / tối cho trang quản trị (nhớ lựa chọn trong trình duyệt).
   Hỗ trợ cả Jazzmin bản Bootstrap 5 (data-bs-theme) lẫn bản cũ (class dark-mode). */
(function () {
    var KEY = "bn-admin-theme";

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

    // Áp dụng sớm để tránh bị nháy trắng khi tải trang
    apply(saved());

    function findNavbarList() {
        var nav = document.querySelector("nav.navbar") || document.querySelector(".main-header, .app-header");
        if (!nav) { return null; }
        var lists = nav.querySelectorAll("ul.navbar-nav");
        return lists.length ? lists[lists.length - 1] : null;   // danh sách cuối = bên phải (menu người dùng)
    }

    function init() {
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

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
