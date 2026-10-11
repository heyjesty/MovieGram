(function () {
    "use strict";

    // Mobile navigation
    var toggle = document.querySelector("[data-menu-toggle]");
    if (toggle) {
        var setOpen = function (open) {
            document.body.classList.toggle("nav-open", open);
            toggle.setAttribute("aria-expanded", String(open));
            toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
        };
        toggle.addEventListener("click", function () {
            setOpen(!document.body.classList.contains("nav-open"));
        });
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") setOpen(false);
        });
        window.matchMedia("(min-width: 1024px)").addEventListener("change", function () { setOpen(false); });
    }

    // Toast messages
    document.querySelectorAll(".toast").forEach(function (toast, i) {
        var hide = function () {
            toast.classList.add("is-hiding");
            setTimeout(function () { toast.remove(); }, 300);
        };
        toast.querySelector("[data-dismiss]").addEventListener("click", hide);
        setTimeout(hide, 5000 + i * 500);
    });

    // Confirm destructive actions
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
        form.addEventListener("submit", function (e) {
            if (!window.confirm(form.getAttribute("data-confirm"))) e.preventDefault();
        });
    });

    // Hero slider
    var slider = document.querySelector("[data-slider]");
    if (slider) {
        var slides = slider.querySelectorAll("[data-slide]");
        var dots = slider.querySelectorAll("[data-dot]");
        var current = 0;
        var timer;
        var show = function (index) {
            slides[current].classList.remove("is-active");
            dots[current].classList.remove("is-active");
            current = (index + slides.length) % slides.length;
            slides[current].classList.add("is-active");
            dots[current].classList.add("is-active");
        };
        var start = function () {
            if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
            clearInterval(timer);
            timer = setInterval(function () { show(current + 1); }, 6000);
        };
        dots.forEach(function (dot) {
            dot.addEventListener("click", function () {
                show(Number(dot.getAttribute("data-dot")));
                start();
            });
        });
        slider.addEventListener("mouseenter", function () { clearInterval(timer); });
        slider.addEventListener("mouseleave", start);

        // Swipe support on touch devices
        var startX = null;
        slider.addEventListener("touchstart", function (e) { startX = e.touches[0].clientX; }, { passive: true });
        slider.addEventListener("touchend", function (e) {
            if (startX === null) return;
            var dx = e.changedTouches[0].clientX - startX;
            if (Math.abs(dx) > 40) { show(current + (dx < 0 ? 1 : -1)); start(); }
            startX = null;
        });
        start();
    }
})();
