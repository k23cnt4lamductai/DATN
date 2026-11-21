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
