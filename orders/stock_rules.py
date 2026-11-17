"""Quy tắc tồn kho theo trạng thái đơn hàng (thuần Python, dễ kiểm thử)."""

CANCELLED = "cancelled"


def stock_action(old_status, new_status):
    """Khi đổi trạng thái đơn thì kho thay đổi thế nào?
    - "restore": đơn bị hủy        -> cộng lại tồn kho
    - "deduct" : đơn đã hủy được khôi phục -> trừ tồn kho lần nữa
    - None     : không ảnh hưởng tới kho
    """
    if old_status is None or old_status == new_status:
        return None
    was_cancelled = old_status == CANCELLED
    now_cancelled = new_status == CANCELLED
    if now_cancelled and not was_cancelled:
        return "restore"
    if was_cancelled and not now_cancelled:
        return "deduct"
    return None
