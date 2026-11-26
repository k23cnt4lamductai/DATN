from datetime import date
from urllib.parse import urlencode

from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.http import url_has_allowed_host_and_scheme

from core.templatetags.vnd import vnd

from .models import Coupon, Order, OrderItem
from .reports import build_customers, build_day_report, build_history

S = Order.Status
# Các nút bấm nhanh theo từng trạng thái: (trạng thái mới, chữ trên nút)
NEXT_STEPS = {
    S.PENDING.value: [(S.CONFIRMED.value, "Xác nhận"), (S.CANCELLED.value, "Hủy")],
    S.CONFIRMED.value: [(S.DELIVERING.value, "Giao hàng"), (S.CANCELLED.value, "Hủy")],
    S.DELIVERING.value: [(S.COMPLETED.value, "Hoàn thành"), (S.CANCELLED.value, "Hủy")],
    S.COMPLETED.value: [],
    S.CANCELLED.value: [(S.PENDING.value, "Khôi phục")],
}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "product_name", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "full_name", "phone", "total_vnd", "payment_method", "is_paid",
        "status_badge", "created_at", "action_buttons",
    )
    list_display_links = ("id", "full_name")
    list_editable = ("is_paid",)
    list_filter = ("status", "payment_method", "is_paid", "created_at")
    search_fields = ("full_name", "phone", "email")
    readonly_fields = ("total", "created_at", "updated_at", "invoice_link")
    inlines = [OrderItemInline]
    actions = ["act_confirm", "act_delivering", "act_completed", "act_cancel"]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalculate_total()  # cập nhật tổng tiền sau khi lưu các dòng chi tiết

    # ---------- Cột trong danh sách ----------
    @admin.display(description="Tổng tiền", ordering="total")
    def total_vnd(self, obj):
        return vnd(obj.total)

    @admin.display(description="Trạng thái", ordering="status")
    def status_badge(self, obj):
        return format_html('<span class="bn-badge bn-st-{}">{}</span>', obj.status, obj.get_status_display())

    @admin.display(description="Thao tác")
    def action_buttons(self, obj):
        buttons = []
        for new_status, label in NEXT_STEPS.get(obj.status, []):
            url = reverse("admin:orders_order_status", args=[obj.pk, new_status])
            if new_status == S.CANCELLED.value:
                css, confirm = "bn-btn-danger", f"Hủy đơn #{obj.pk}? Tồn kho sẽ được hoàn lại."
            elif new_status == S.PENDING.value:
                css, confirm = "bn-btn-ghost", f"Khôi phục đơn #{obj.pk}? Tồn kho sẽ bị trừ lại."
            else:
                css, confirm = "", ""
            buttons.append(format_html(
                '<button type="button" class="bn-btn {}" data-bn-post="{}" data-confirm="{}">{}</button>',
                css, url, confirm, label,
            ))
        buttons.append(format_html(
            '<a class="bn-btn bn-btn-ghost" href="{}?print=1" target="_blank" rel="noopener">In</a>',
            reverse("admin:orders_order_invoice", args=[obj.pk]),
        ))
        return format_html_join("", "{}", ((b,) for b in buttons))

    @admin.display(description="Hóa đơn")
    def invoice_link(self, obj):
        if not obj or not obj.pk:
            return "—"
        return format_html(
            '<a class="bn-btn bn-btn-ghost" href="{}?print=1" target="_blank" rel="noopener">🖨 In hóa đơn</a>',
            reverse("admin:orders_order_invoice", args=[obj.pk]),
        )

    # ---------- Thao tác hàng loạt ----------
    def _bulk_status(self, request, queryset, new_status):
        label = Order.Status(new_status).label
        done, errors = 0, []
        for order in queryset:
            before = order.status
            try:
                order.change_status(new_status)
            except ValidationError as exc:
                errors.append(f"Đơn #{order.pk}: " + " ".join(exc.messages))
                continue
            if before != new_status:
                self.log_change(request, order, f"Đổi trạng thái sang {label}")
                done += 1
        if done:
            self.message_user(request, f"Đã chuyển {done} đơn sang “{label}”.", "success")
        for text in errors[:5]:
            self.message_user(request, text, "error")

    @admin.action(description="Xác nhận các đơn đã chọn")
    def act_confirm(self, request, queryset):
        self._bulk_status(request, queryset, S.CONFIRMED.value)

    @admin.action(description="Chuyển các đơn đã chọn sang “Đang giao”")
    def act_delivering(self, request, queryset):
        self._bulk_status(request, queryset, S.DELIVERING.value)

    @admin.action(description="Đánh dấu các đơn đã chọn “Hoàn thành”")
    def act_completed(self, request, queryset):
        self._bulk_status(request, queryset, S.COMPLETED.value)

    @admin.action(description="Hủy các đơn đã chọn (hoàn lại tồn kho)")
    def act_cancel(self, request, queryset):
        self._bulk_status(request, queryset, S.CANCELLED.value)

    # ---------- Các trang tùy chỉnh trong admin ----------
    def get_urls(self):
        wrap = self.admin_site.admin_view
        custom = [
            path("bao-cao/", wrap(self.report_view), name="orders_order_report"),
            path("khach-hang/", wrap(self.customers_view), name="orders_order_customers"),
            path("<int:pk>/in/", wrap(self.invoice_view), name="orders_order_invoice"),
            path("<int:pk>/trang-thai/<str:new_status>/", wrap(self.status_view), name="orders_order_status"),
        ]
        return custom + super().get_urls()

    def report_view(self, request):
        """Báo cáo doanh thu theo ngày: /admin/orders/order/bao-cao/"""
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

    def customers_view(self, request):
        """Danh sách khách hàng: số đơn, tổng chi tiêu."""
        if not self.has_view_permission(request):
            raise PermissionDenied

        q = request.GET.get("q", "").strip()
        rows = build_customers(q)
        page = Paginator(rows, 20).get_page(request.GET.get("page"))
        changelist = reverse("admin:orders_order_changelist")
        for row in page.object_list:
            if row["user_id"]:
                row["orders_url"] = f"{changelist}?{urlencode({'user': row['user_id']})}"
            else:
                row["orders_url"] = f"{changelist}?{urlencode({'q': row['phone'] or row['name']})}"

        context = {
            **self.admin_site.each_context(request),
            "title": "Khách hàng",
            "opts": self.model._meta,
            "q": q,
            "page": page,
            "total_customers": len(rows),
            "members": sum(1 for r in rows if r["kind"] == "member"),
            "guests": sum(1 for r in rows if r["kind"] == "guest"),
            "total_spent": sum((r["spent"] for r in rows), 0),
        }
        return TemplateResponse(request, "orders/admin_customers.html", context)

    def invoice_view(self, request, pk):
        """Hóa đơn in được: /admin/orders/order/<id>/in/"""
        if not self.has_view_permission(request):
            raise PermissionDenied
        order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)
        return TemplateResponse(request, "orders/invoice.html", {
            "order": order,
            "items": order.items.all(),
            "auto_print": request.GET.get("print") == "1",
        })

    def status_view(self, request, pk, new_status):
        """Nút đổi trạng thái nhanh (chỉ nhận POST, có kiểm tra CSRF)."""
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        if not self.has_change_permission(request):
            raise PermissionDenied

        order = get_object_or_404(Order, pk=pk)
        before = order.status
        try:
            order.change_status(new_status)
        except ValidationError as exc:
            self.message_user(request, f"Đơn #{order.pk}: " + " ".join(exc.messages), "error")
        else:
            if before != order.status:
                label = order.get_status_display()
                self.log_change(request, order, f"Đổi trạng thái sang {label}")
                self.message_user(request, f"Đơn #{order.pk}: {label}.", "success")

        target = request.META.get("HTTP_REFERER", "")
        if not url_has_allowed_host_and_scheme(
            target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            target = reverse("admin:orders_order_changelist")
        return redirect(target)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "muc_giam", "min_order", "luot_dung", "ends_at", "is_active")
    list_editable = ("is_active",)
    list_filter = ("kind", "is_active")
    search_fields = ("code", "description")
    readonly_fields = ("used_count",)

    @admin.display(description="Mức giảm")
    def muc_giam(self, obj):
        if obj.kind == Coupon.Kind.PERCENT:
            text = f"{obj.value}%"
            if obj.max_discount:
                text += f" (tối đa {vnd(obj.max_discount)})"
            return text
        return vnd(obj.value)

    @admin.display(description="Lượt dùng")
    def luot_dung(self, obj):
        return f"{obj.used_count}/{obj.usage_limit}" if obj.usage_limit is not None else f"{obj.used_count}/∞"


# ---- Tên trang quản trị + trang tổng quan (doanh thu, đơn mới, bánh sắp hết) ----
admin.site.site_header = "Quản trị Tài Bakery"
admin.site.site_title = "Tài Bakery"
admin.site.index_title = "Tổng quan"
admin.site.index_template = "orders/admin_index.html"
