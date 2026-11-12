from datetime import datetime, time, timedelta

from django import template
from django.db.models import Sum
from django.utils import timezone

from orders.models import Order
from products.models import Product

register = template.Library()

LOW_STOCK = 5  # tồn kho <= số này thì cảnh báo sắp hết


def _day_range(day):
    """[00:00 ngày đó, 00:00 ngày hôm sau) theo múi giờ của project.
    Dùng khoảng thời gian thay vì __date để không phụ thuộc bảng múi giờ của MySQL."""
    start = timezone.make_aware(datetime.combine(day, time.min))
    return start, start + timedelta(days=1)


def _short_money(value):
    value = float(value)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}tr"
    if value >= 1_000:
        return f"{value / 1_000:.0f}k"
    return f"{value:.0f}"


@register.simple_tag
def dashboard_data():
    today = timezone.localdate()
    valid = Order.objects.exclude(status=Order.Status.CANCELLED)  # doanh thu không tính đơn đã hủy

    def revenue(qs):
        return qs.aggregate(s=Sum("total"))["s"] or 0

    t0, t1 = _day_range(today)
    m0, _ = _day_range(today.replace(day=1))
    today_qs = valid.filter(created_at__gte=t0, created_at__lt=t1)
    month_qs = valid.filter(created_at__gte=m0, created_at__lt=t1)

    # Doanh thu 7 ngày gần nhất (1 truy vấn, gom theo ngày bằng Python)
    by_day = {today - timedelta(days=i): 0 for i in range(6, -1, -1)}
    w0, _ = _day_range(today - timedelta(days=6))
    for created, total in valid.filter(created_at__gte=w0, created_at__lt=t1).values_list("created_at", "total"):
        day = timezone.localtime(created).date()
        if day in by_day:
            by_day[day] += total
    peak = max(by_day.values())
    chart = [
        {
            "label": day.strftime("%d/%m"),
            "iso": day.isoformat(),
            "value": value,
            "short": _short_money(value),
            "height": max(round(value * 100 / peak), 4) if value else 0,
        }
        for day, value in by_day.items()
    ]

    low_stock_qs = Product.objects.filter(is_available=True, stock__lte=LOW_STOCK)

    return {
        "revenue_today": revenue(today_qs),
        "orders_today": today_qs.count(),
        "revenue_month": revenue(month_qs),
        "orders_month": month_qs.count(),
        "pending": Order.objects.filter(status=Order.Status.PENDING).count(),
        "low_stock_limit": LOW_STOCK,
        "low_stock_count": low_stock_qs.count(),
        "low_stock": low_stock_qs.order_by("stock", "name")[:6],
        "recent_orders": Order.objects.order_by("-created_at")[:6],
        "chart": chart,
        "week_total": sum(by_day.values()),
    }
