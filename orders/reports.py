"""Tính số liệu báo cáo doanh thu theo ngày từ bảng đơn hàng (không cần lưu thêm bảng nào)."""
from datetime import datetime, time, timedelta

from django.utils import timezone

from .models import Order, OrderItem


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


# ---------------------------------------------------------------- Biểu đồ trang Tổng quan
def _valid_items(today, days):
    """Các dòng hàng của đơn không bị hủy trong `days` ngày gần nhất (tính đến hết hôm nay)."""
    first = today - timedelta(days=days - 1)
    start, _ = day_range(first)
    _, end = day_range(today)
    return OrderItem.objects.filter(
        order__created_at__gte=start, order__created_at__lt=end
    ).exclude(order__status=Order.Status.CANCELLED)


def top_products(today, days=30, limit=5):
    """Bánh bán chạy nhất (theo số lượng) trong `days` ngày gần nhất."""
    totals = {}
    for name, quantity, price in _valid_items(today, days).values_list("product_name", "quantity", "price"):
        row = totals.setdefault(name, {"name": name, "quantity": 0, "revenue": 0})
        row["quantity"] += quantity
        row["revenue"] += price * quantity
    rows = sorted(totals.values(), key=lambda r: (-r["quantity"], r["name"]))[:limit]
    peak = rows[0]["quantity"] if rows else 0
    for row in rows:
        row["percent"] = max(round(row["quantity"] * 100 / peak), 4) if peak else 0
    return rows


def revenue_by_category(today, days=30):
    """Doanh thu theo danh mục trong `days` ngày gần nhất."""
    totals = {}
    for category, quantity, price in _valid_items(today, days).values_list(
        "product__category__name", "quantity", "price"
    ):
        name = category or "Khác (sản phẩm đã xóa)"
        totals[name] = totals.get(name, 0) + price * quantity
    grand = sum(totals.values())
    return [
        {
            "name": name,
            "revenue": revenue,
            "share": round(revenue * 100 / grand) if grand else 0,
            "bar": max(round(revenue * 100 / grand), 3) if grand else 0,
        }
        for name, revenue in sorted(totals.items(), key=lambda kv: -kv[1])
    ]


# ---------------------------------------------------------------- Danh sách khách hàng
def build_customers(query=""):
    """Khách thành viên (có tài khoản) + khách vãng lai (gom theo số điện thoại),
    kèm số đơn và tổng chi tiêu (không tính đơn đã hủy). Sắp xếp: chi tiêu nhiều nhất trước."""
    from django.contrib.auth import get_user_model

    users = {u.pk: u for u in get_user_model().objects.all()}
    rows = {}
    for user in users.values():
        rows[("u", user.pk)] = {
            "kind": "member", "user_id": user.pk,
            "name": user.get_full_name() or user.get_username(),
            "email": user.email or "", "phone": "",
            "orders": 0, "cancelled": 0, "spent": 0, "last": None,
            "is_staff": user.is_staff,
        }

    orders = Order.objects.order_by("created_at").values_list(
        "user_id", "full_name", "phone", "status", "total", "created_at"
    )
    for user_id, full_name, phone, status, total, created in orders:
        if user_id in users:
            key = ("u", user_id)
        else:
            digits = "".join(ch for ch in phone if ch.isdigit())
            key = ("g", digits or full_name.strip().lower())
            if key not in rows:
                rows[key] = {
                    "kind": "guest", "user_id": None, "name": full_name, "email": "",
                    "phone": phone, "orders": 0, "cancelled": 0, "spent": 0, "last": None,
                    "is_staff": False,
                }
        row = rows[key]
        row["phone"] = phone                       # số điện thoại ở đơn gần nhất
        if row["kind"] == "guest":
            row["name"] = full_name
        if status == Order.Status.CANCELLED:
            row["cancelled"] += 1
        else:
            row["orders"] += 1
            row["spent"] += total
        row["last"] = created

    result = list(rows.values())
    if query:
        q = query.strip().lower()
        result = [r for r in result if q in r["name"].lower() or q in r["phone"] or q in r["email"].lower()]
    result.sort(key=lambda r: (-r["spent"], -r["orders"], r["name"].lower()))
    return result
