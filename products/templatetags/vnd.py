from django import template

register = template.Library()


@register.filter
def vnd(value):
    """Định dạng tiền Việt: 120000 -> 120.000đ"""
    try:
        return f"{int(value):,}".replace(",", ".") + "đ"
    except (TypeError, ValueError):
        return value
