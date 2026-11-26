from urllib.parse import urlencode

from django import template

from config.shop_info import SHOP_INFO

register = template.Library()


@register.simple_tag
def bank_transfer(order):
    """Thông tin chuyển khoản + mã QR VietQR cho đơn chọn 'Chuyển khoản' (None nếu không áp dụng)."""
    bank = SHOP_INFO.get("bank")
    if not bank or order.payment_method != order.PaymentMethod.BANK:
        return None
    content = f"TAIBAKERY{order.pk}"
    query = urlencode({"amount": int(order.total), "addInfo": content, "accountName": bank["account_name"]})
    return {
        **bank,
        "content": content,
        "qr_url": f"https://img.vietqr.io/image/{bank['bank_id']}-{bank['account_no']}-compact2.png?{query}",
    }
