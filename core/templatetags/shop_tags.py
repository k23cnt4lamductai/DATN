from django import template

from config.shop_info import SHOP_INFO

register = template.Library()


@register.simple_tag
def shop_info():
    """Thông tin cửa hàng từ config/shop_info.py."""
    return SHOP_INFO


@register.filter
def digits(value):
    """'0900 000 000' -> '0900000000' (dùng cho liên kết tel:)."""
    return "".join(ch for ch in str(value) if ch.isdigit() or ch == "+")


@register.simple_tag
def nav_categories():
    """Danh mục bánh (dùng cho menu 'Sản phẩm', dải danh mục và thẻ danh mục ở trang chủ)."""
    from products.models import Category
    return list(Category.objects.all())


@register.simple_tag
def footer_branches():
    """Các chi nhánh đang hoạt động."""
    from stores.models import Branch
    return list(Branch.objects.filter(is_active=True).order_by("id"))


@register.filter
def cat_icon(name):
    """Biểu tượng gợi ý theo tên danh mục."""
    n = str(name).lower()
    for keys, icon in (
        (("sinh nhật", "bánh kem", "kem"), "🎂"),
        (("mì", "mỳ", "bread"), "🥖"),
        (("cupcake",), "🧁"),
        (("cookie", "quy", "khô"), "🍪"),
        (("socola", "chocolate", "chocolat"), "🍫"),
    ):
        if any(k in n for k in keys):
            return icon
    return "🍰"


@register.simple_tag
def latest_articles(count=3):
    """Bài tin tức / khuyến mại mới nhất (cho trang chủ)."""
    from content.models import Article
    return list(Article.objects.published()[:count])


@register.filter
def lines(value):
    """Tách văn bản nhiều dòng thành danh sách ý (bỏ gạch đầu dòng nếu có)."""
    return [ln.strip().lstrip("-•*· ").strip() for ln in str(value).splitlines() if ln.strip()]
