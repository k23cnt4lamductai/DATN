from django import template

from orders.cart import CART_SESSION_KEY

register = template.Library()


@register.simple_tag(takes_context=True)
def cart_count(context):
    """Tổng số bánh trong giỏ, dùng hiển thị trên đầu trang."""
    request = context.get("request")
    if request is None:
        return 0
    return sum(request.session.get(CART_SESSION_KEY, {}).values())
