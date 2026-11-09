from django.contrib import admin
from django.db.models import Avg, Count, Q
from django.utils.html import format_html

from .models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "category", "price", "stock", "is_available", "rating_info")
    list_display_links = ("thumb", "name")
    list_editable = ("price", "stock", "is_available")   # sửa nhanh ngay trên danh sách
    list_filter = ("category", "is_available")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = 20
    readonly_fields = ("image_preview",)

    def get_queryset(self, request):
        visible = Q(reviews__is_visible=True)
        return super().get_queryset(request).annotate(
            _avg=Avg("reviews__rating", filter=visible),
            _n=Count("reviews", filter=visible),
        )

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
            return format_html(
                '<img src="{}" style="max-width:240px;border-radius:10px;">', obj.image.url
            )
        return "Chưa có ảnh"

    @admin.display(description="Đánh giá", ordering="_avg")
    def rating_info(self, obj):
        if obj._n:
            return f"{obj._avg:.1f} ★ ({obj._n})"
        return "—"


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
