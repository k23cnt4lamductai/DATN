from django.contrib import admin
from django.contrib.admin import helpers
from django.db.models import Avg, Count, F, Q
from django.template.response import TemplateResponse
from django.utils.html import format_html

from .admin_forms import DiscountForm, RestockForm
from .constants import LOW_STOCK
from .models import Category, Product, Review
from .pricing import calc_new_price


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class StockFilter(admin.SimpleListFilter):
    title = "Tồn kho"
    parameter_name = "kho"

    def lookups(self, request, model_admin):
        return [
            ("out", "Hết hàng"),
            ("low", f"Sắp hết (còn ≤ {LOW_STOCK})"),
            ("ok", "Còn đủ hàng"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "out":
            return queryset.filter(stock=0)
        if self.value() == "low":
            return queryset.filter(stock__gt=0, stock__lte=LOW_STOCK)
        if self.value() == "ok":
            return queryset.filter(stock__gt=LOW_STOCK)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "category", "price", "stock", "stock_badge", "is_available", "rating_info")
    list_display_links = ("thumb", "name")
    list_editable = ("price", "stock", "is_available")   # sửa nhanh ngay trên danh sách
    list_filter = ("category", "is_available", StockFilter)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 20
    readonly_fields = ("image_preview",)
    actions = ["act_hide", "act_show", "act_price", "act_restock"]

    def get_queryset(self, request):
        visible = Q(reviews__is_visible=True)
        return super().get_queryset(request).annotate(
            _avg=Avg("reviews__rating", filter=visible),
            _n=Count("reviews", filter=visible),
        )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ("price", "stock"):
            # Gắn class chung để CSS làm các ô nhập số đều, gọn
            field.widget.attrs["class"] = (field.widget.attrs.get("class", "") + " bn-num").strip()
            field.widget.attrs["min"] = 0
        return field

    # ---------- Cột trong danh sách ----------
    @admin.display(description="Ảnh")
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:64px;height:48px;object-fit:cover;border-radius:6px;">',
                obj.image.url,
            )
        return "—"

    @admin.display(description="Xem trước ảnh")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="max-width:240px;border-radius:10px;">', obj.image.url)
        return "Chưa có ảnh"

    @admin.display(description="Đánh giá", ordering="_avg")
    def rating_info(self, obj):
        if obj._n:
            return f"{obj._avg:.1f} ★ ({obj._n})"
        return "—"

    @admin.display(description="Tình trạng kho", ordering="stock")
    def stock_badge(self, obj):
        if obj.stock == 0:
            css, text = "bn-st-out", "Hết hàng"
        elif obj.stock <= LOW_STOCK:
            css, text = "bn-st-low", f"Sắp hết ({obj.stock})"
        else:
            css, text = "bn-st-ok", "Còn hàng"
        return format_html('<span class="bn-badge {}">{}</span>', css, text)

    # ---------- Thao tác hàng loạt ----------
    @staticmethod
    def _ids(queryset):
        return list(queryset.values_list("pk", flat=True))

    def _confirm_page(self, request, queryset, form, action_name, title, intro):
        """Trang xác nhận có ô nhập (phần trăm, số lượng...) trước khi áp dụng."""
        return TemplateResponse(request, "products/admin_bulk_form.html", {
            **self.admin_site.each_context(request),
            "title": title,
            "opts": self.model._meta,
            "intro": intro,
            "form": form,
            "products": queryset,
            "action_name": action_name,
            "selected": request.POST.getlist(helpers.ACTION_CHECKBOX_NAME),
            "select_across": request.POST.get("select_across", "0"),
            "cancel_url": request.get_full_path(),
        })

    @admin.action(description="Ẩn khỏi cửa hàng")
    def act_hide(self, request, queryset):
        n = Product.objects.filter(pk__in=self._ids(queryset)).update(is_available=False)
        self.message_user(request, f"Đã ẩn {n} sản phẩm khỏi cửa hàng.", "success")

    @admin.action(description="Hiện lên cửa hàng")
    def act_show(self, request, queryset):
        n = Product.objects.filter(pk__in=self._ids(queryset)).update(is_available=True)
        self.message_user(request, f"Đã hiện {n} sản phẩm lên cửa hàng.", "success")

    @admin.action(description="Giảm / tăng giá theo %%…")
    def act_price(self, request, queryset):
        if "apply" in request.POST:
            form = DiscountForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                changed = 0
                for product in Product.objects.filter(pk__in=self._ids(queryset)):
                    new_price = calc_new_price(product.price, data["percent"], data["direction"], data["round_to"])
                    if new_price != product.price:
                        product.price = new_price
                        product.save(update_fields=["price", "updated_at"])
                        changed += 1
                verb = "Giảm" if data["direction"] == "down" else "Tăng"
                self.message_user(request, f"{verb} {data['percent']}% giá cho {changed} sản phẩm.", "success")
                return None
        else:
            form = DiscountForm()
        return self._confirm_page(
            request, queryset, form, "act_price", "Giảm / tăng giá hàng loạt",
            "Giá hiện tại sẽ được thay đổi trực tiếp và không có giá gốc để khôi phục. "
            "Hãy kiểm tra danh sách bên dưới trước khi áp dụng.",
        )

    @admin.action(description="Nhập thêm hàng (cộng vào tồn kho)…")
    def act_restock(self, request, queryset):
        if "apply" in request.POST:
            form = RestockForm(request.POST)
            if form.is_valid():
                qty = form.cleaned_data["quantity"]
                n = Product.objects.filter(pk__in=self._ids(queryset)).update(stock=F("stock") + qty)
                self.message_user(request, f"Đã nhập thêm {qty} vào tồn kho của {n} sản phẩm.", "success")
                return None
        else:
            form = RestockForm()
        return self._confirm_page(
            request, queryset, form, "act_restock", "Nhập thêm hàng",
            "Số lượng nhập sẽ được cộng vào tồn kho của từng sản phẩm bên dưới.",
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "short_comment", "is_visible", "created_at")
    list_editable = ("is_visible",)          # bỏ tick để ẩn nhận xét không phù hợp
    list_filter = ("rating", "is_visible", "created_at")
    search_fields = ("product__name", "user__username", "comment")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Nhận xét")
    def short_comment(self, obj):
        return (obj.comment[:60] + "…") if len(obj.comment) > 60 else obj.comment
