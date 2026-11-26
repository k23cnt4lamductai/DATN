/* Băng chuyền sản phẩm: tự lướt, tạm dừng khi rê chuột / chạm, có nút trước - sau. */
(function () {
    var DELAY = 2200;
    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function init(root) {
        var track = root.querySelector(".car-track");
        var items = track.querySelectorAll(".car-item");
        var prev = root.querySelector(".car-btn.prev");
        var next = root.querySelector(".car-btn.next");
        var timer = null, paused = false, visible = true;

        function overflow() { return track.scrollWidth - track.clientWidth > 4; }
        function step() {
            if (items.length < 2) return track.clientWidth;
            return items[1].offsetLeft - items[0].offsetLeft;
        }
        function atEnd() { return track.scrollLeft + track.clientWidth >= track.scrollWidth - 4; }

        function go(dir) {
            if (!overflow()) return;
            if (dir > 0) {
                if (atEnd()) track.scrollTo({ left: 0, behavior: "smooth" });
                else track.scrollBy({ left: step(), behavior: "smooth" });
            } else {
                if (track.scrollLeft <= 4) track.scrollTo({ left: track.scrollWidth, behavior: "smooth" });
                else track.scrollBy({ left: -step(), behavior: "smooth" });
            }
        }
        function stop() { if (timer) { clearInterval(timer); timer = null; } }
        function start() {
            stop();
            if (reduceMotion || paused || !visible || document.hidden || !overflow()) return;
            timer = setInterval(function () { go(1); }, DELAY);
        }
        function refresh() {
            root.classList.toggle("no-scroll", !overflow());
            start();
        }

        if (prev) prev.addEventListener("click", function () { go(-1); start(); });
        if (next) next.addEventListener("click", function () { go(1); start(); });

        root.addEventListener("mouseenter", function () { paused = true; stop(); });
        root.addEventListener("mouseleave", function () { paused = false; start(); });
        root.addEventListener("focusin", function () { paused = true; stop(); });
        root.addEventListener("focusout", function () { paused = false; start(); });
        root.addEventListener("touchstart", function () { paused = true; stop(); }, { passive: true });
        root.addEventListener("touchend", function () { setTimeout(function () { paused = false; start(); }, 4000); }, { passive: true });
        document.addEventListener("visibilitychange", start);
        window.addEventListener("resize", refresh);

        if ("IntersectionObserver" in window) {
            new IntersectionObserver(function (entries) {
                visible = entries[0].isIntersecting;
                start();
            }).observe(root);
        }
        refresh();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-carousel]").forEach(init);
    });
})();
