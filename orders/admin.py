from datetime import date

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from .models import Order, OrderItem
from .reports import build_day_report, build_history


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "product_name", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "total", "payment_method", "status", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("full_name", "phone", "email")
    list_editable = ("status",)
    readonly_fields = ("total", "created_at", "updated_at")
    inlines = [OrderItemInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalculate_total()  # cập nhật tổng tiền sau khi lưu các dòng chi tiết

    # ---------- Báo cáo doanh thu theo ngày: /admin/orders/order/bao-cao/ ----------
    def get_urls(self):
        custom = [
            path("bao-cao/", self.admin_site.admin_view(self.report_view), name="orders_order_report"),
        ]
        return custom + super().get_urls()

    def report_view(self, request):
        if not self.has_view_permission(request):
            raise PermissionDenied

        today = timezone.localdate()
        try:
            day = date.fromisoformat(request.GET.get("date", ""))
        except ValueError:
            day = today  # không chọn ngày (hoặc sai định dạng) -> hôm nay

        context = {
            **self.admin_site.each_context(request),
            "title": "Báo cáo doanh thu theo ngày",
            "opts": self.model._meta,
            "day": day,
            "today": today,
            "is_today": day == today,
            "prev_day": day.fromordinal(day.toordinal() - 1),
            "next_day": day.fromordinal(day.toordinal() + 1) if day < today else None,
            "report": build_day_report(day),
            "history": build_history(today, days=30),
        }
        return TemplateResponse(request, "orders/admin_report.html", context)


# ---- Tên trang quản trị + trang tổng quan (doanh thu, đơn mới, bánh sắp hết) ----
admin.site.site_header = "Quản trị Tiệm Bánh Ngọt"
admin.site.site_title = "Tiệm Bánh Ngọt"
admin.site.index_title = "Tổng quan"
admin.site.index_template = "orders/admin_index.html"
