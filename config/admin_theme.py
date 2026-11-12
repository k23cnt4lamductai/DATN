"""Cấu hình giao diện trang quản trị (thư viện django-jazzmin)."""

JAZZMIN_SETTINGS = {
    # --- Tên / thương hiệu ---
    "site_title": "Quản trị Tiệm Bánh Ngọt",
    "site_header": "Tiệm Bánh Ngọt",
    "site_brand": "🧁 Tiệm Bánh Ngọt",
    "welcome_sign": "Chào mừng đến trang quản lý Tiệm Bánh Ngọt",
    "copyright": "Tiệm Bánh Ngọt",
    "language_chooser": False,

    # --- Tìm nhanh trên thanh trên cùng ---
    "search_model": ["products.Product", "orders.Order"],

    # --- Thanh menu trên ---
    "topmenu_links": [
        {"name": "🏠 Về trang chủ", "url": "/"},
        {"name": "Tổng quan", "url": "admin:index"},
        {"name": "Đơn hàng", "model": "orders.Order"},
        {"name": "Báo cáo doanh thu", "url": "admin:orders_order_report"},
        {"name": "Sản phẩm", "model": "products.Product"},
    ],
    "usermenu_links": [
        {"name": "Về trang chủ website", "url": "/"},
    ],
    "index_title": "Tổng quan",

    # --- Menu bên cạnh ---
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": [
        "orders", "orders.order", "orders.orderitem",
        "products", "products.product", "products.category", "products.review",
        "auth",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "orders": "fas fa-receipt",
        "orders.order": "fas fa-receipt",
        "orders.orderitem": "fas fa-list",
        "products": "fas fa-birthday-cake",
        "products.product": "fas fa-birthday-cake",
        "products.category": "fas fa-tags",
        "products.review": "fas fa-star",
    },
    "custom_links": {
        "orders": [
            {
                "name": "Báo cáo doanh thu",
                "url": "admin:orders_order_report",
                "icon": "fas fa-chart-line",
                "permissions": ["orders.view_order"],
            },
        ],
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # --- Màu hồng - kem giống website (file CSS riêng) ---
    "custom_css": "products/css/admin_custom.css",
    "custom_js": "products/js/admin_theme.js",   # nút đổi giao diện sáng / tối

    "changeform_format": "single",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-pink",
    "accent": "accent-pink",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-pink",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "default_theme_mode": "light",   # Jazzmin 3.0.3+: không tự chuyển tối theo máy
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
