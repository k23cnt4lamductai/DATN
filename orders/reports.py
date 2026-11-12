"""Tính số liệu báo cáo doanh thu theo ngày từ bảng đơn hàng (không cần lưu thêm bảng nào)."""
from datetime import datetime, time, timedelta

from django.utils import timezone

from .models import Order


def day_range(day):
    """[00:00 của ngày đó, 00:00 ngày hôm sau) theo múi giờ của project.
    Dùng khoảng thời gian thay vì __date để không phụ thuộc bảng múi giờ của MySQL."""
    start = timezone.make_aware(datetime.combine(day, time.min))
    return start, start + timedelta(days=1)


def build_day_report(day):
    """Toàn bộ số liệu của MỘT ngày: số đơn, doanh thu, chi tiết từng đơn, bánh bán được."""
    start, end = day_range(day)
    orders = list(
        Order.objects.filter(created_at__gte=start, created_at__lt=end)
        .order_by("created_at")
        .prefetch_related("items")
    )
    valid = [o for o in orders if o.status != Order.Status.CANCELLED]  # không tính đơn đã hủy

    status_rows = [
        {"value": value, "label": label, "count": sum(1 for o in orders if o.status == value)}
        for value, label in Order.Status.choices
    ]

    products = {}
    for order in valid:
        for item in order.items.all():
            row = products.setdefault(
                item.product_name, {"name": item.product_name, "quantity": 0, "revenue": 0}
            )
            row["quantity"] += item.quantity
            row["revenue"] += item.subtotal
    product_rows = sorted(products.values(), key=lambda r: (-r["quantity"], r["name"]))

    return {
        "orders": orders,
        "order_count": len(valid),
        "cancelled_count": len(orders) - len(valid),
        "revenue": sum((o.total for o in valid), 0),
        "items_sold": sum(r["quantity"] for r in product_rows),
        "status_rows": status_rows,
        "product_rows": product_rows,
    }


def build_history(today, days=30):
    """Doanh thu từng ngày trong `days` ngày gần nhất (mới nhất ở trên)."""
    first = today - timedelta(days=days - 1)
    start, _ = day_range(first)
    _, end = day_range(today)

    buckets = {first + timedelta(days=i): {"orders": 0, "cancelled": 0, "revenue": 0} for i in range(days)}
    rows = Order.objects.filter(created_at__gte=start, created_at__lt=end).values_list(
        "created_at", "total", "status"
    )
    for created, total, status in rows:
        bucket = buckets.get(timezone.localtime(created).date())
        if bucket is None:
            continue
        if status == Order.Status.CANCELLED:
            bucket["cancelled"] += 1
        else:
            bucket["orders"] += 1
            bucket["revenue"] += total

    history = [{"date": d, **b} for d, b in sorted(buckets.items(), reverse=True)]
    return {
        "rows": history,
        "total_orders": sum(h["orders"] for h in history),
        "total_revenue": sum((h["revenue"] for h in history), 0),
        "days": days,
    }
