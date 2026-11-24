from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, IntegerField, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.views.decorators.http import require_POST

from core.templatetags.vnd import vnd
from orders.models import Order, OrderItem

from .forms import ReviewForm
from .listing import DEFAULT_SORT, PAGE_SIZE, SORTS, make_url, page_items, parse_filters
from .models import Category, Product, Review


def with_ratings(queryset):
    """Gắn điểm trung bình (avg_rating) và số lượt đánh giá (review_count) vào từng sản phẩm."""
    visible = Q(reviews__is_visible=True)
    return queryset.annotate(
        avg_rating=Avg("reviews__rating", filter=visible),
        review_count=Count("reviews", filter=visible),
    )


def _bought_items(product):
    return OrderItem.objects.filter(product=product).exclude(order__status=Order.Status.CANCELLED)


def review_permission(user, product):
    """(được_phép, lý_do). Mặc định chỉ khách đã mua (đơn chưa hủy) mới được đánh giá.
    Muốn cho mọi tài khoản đánh giá: đặt REVIEW_REQUIRE_PURCHASE = False trong settings.py."""
    if not user.is_authenticated:
        return False, "login"
    if getattr(settings, "REVIEW_REQUIRE_PURCHASE", True):
        if not _bought_items(product).filter(order__user=user).exists():
            return False, "purchase"
    return True, ""


def with_sold(queryset):
    """Gắn số bánh đã bán (sold) = tổng số lượng trong các đơn chưa hủy."""
    sold = (
        OrderItem.objects.filter(product=OuterRef("pk"))
        .exclude(order__status=Order.Status.CANCELLED)
        .values("product").order_by()
        .annotate(total=Sum("quantity")).values("total")
    )
    return queryset.annotate(sold=Coalesce(Subquery(sold, output_field=IntegerField()), Value(0)))


def _ordering(sort):
    if sort == "popular":
        return ["-sold", "-created_at", "-pk"]
    if sort == "rating":
        return [F("avg_rating").desc(nulls_last=True), "-review_count", "-created_at"]
    if sort == "price_asc":
        return ["price", "name"]
    if sort == "price_desc":
        return ["-price", "name"]
    return ["-created_at", "-pk"]


def home(request):
    flt = parse_filters(request.GET)
    items = list(request.GET.items())
    base = request.path
    anchor = "#san-pham"

    products = Product.objects.filter(is_available=True).select_related("category")
    if flt["category"]:
        products = products.filter(category__slug=flt["category"])
    if flt["q"]:
        products = products.filter(name__icontains=flt["q"])
    if flt["min_price"] is not None:
        products = products.filter(price__gte=flt["min_price"])
    if flt["max_price"] is not None:
        products = products.filter(price__lte=flt["max_price"])
    products = with_sold(with_ratings(products)).order_by(*_ordering(flt["sort"]))

    paginator = Paginator(products, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Liên kết giữ nguyên các bộ lọc khác khi đổi danh mục / đổi trang
    category_links = [
        {"name": c.name, "url": make_url(base, items, category=c.slug) + anchor, "active": c.slug == flt["category"]}
        for c in Category.objects.all()
    ]
    page_links = []
    for number in page_items(page_obj.number, paginator.num_pages):
        if number is None:
            page_links.append({"gap": True})
        else:
            page_links.append({
                "num": number, "current": number == page_obj.number,
                "url": make_url(base, items, page=None if number == 1 else number) + anchor,
            })

    has_price = flt["min_price"] is not None or flt["max_price"] is not None
    filters_active = has_price or flt["sort"] != DEFAULT_SORT
    summary = []
    if flt["min_price"] is not None and flt["max_price"] is not None:
        summary.append(f"giá từ {vnd(flt['min_price'])} đến {vnd(flt['max_price'])}")
    elif flt["min_price"] is not None:
        summary.append(f"giá từ {vnd(flt['min_price'])}")
    elif flt["max_price"] is not None:
        summary.append(f"giá đến {vnd(flt['max_price'])}")
    if flt["sort"] != DEFAULT_SORT:
        summary.append("sắp xếp: " + dict(SORTS)[flt["sort"]].lower())

    # Mục "Bánh bán chạy" / "Bánh mới": chỉ hiện ở trang chủ nguyên bản (chưa lọc, trang 1)
    show_highlights = (
        not (flt["category"] or flt["q"] or has_price)
        and flt["sort"] == DEFAULT_SORT and page_obj.number == 1
    )
    bestsellers, newest, testimonials = [], [], []
    if show_highlights:
        shelf = with_sold(with_ratings(Product.objects.filter(is_available=True).select_related("category")))
        bestsellers = list(shelf.filter(sold__gt=0).order_by("-sold", "-created_at")[:4])
        newest = list(shelf.order_by("-created_at", "-pk")[:4])
        # "Khách hàng nói gì": đánh giá 4-5 sao có nhận xét, lấy sẵn từ bảng Review
        testimonials = list(
            Review.objects.filter(is_visible=True, rating__gte=4, product__is_available=True)
            .exclude(comment="")
            .select_related("user", "product")
            .order_by("-rating", "-created_at")[:3]
        )

    return render(request, "products/home.html", {
        "products": page_obj,
        "page_obj": page_obj,
        "total_count": paginator.count,
        "page_links": page_links,
        "prev_url": make_url(base, items, page=None if page_obj.number == 2 else page_obj.number - 1) + anchor if page_obj.has_previous() else "",
        "next_url": make_url(base, items, page=page_obj.number + 1) + anchor if page_obj.has_next() else "",
        "category_links": category_links,
        "all_url": make_url(base, items, category=None) + anchor,
        "reset_url": make_url(base, items, sort=None, min_price=None, max_price=None) + anchor,
        "popular_url": make_url(base, [], sort="popular") + anchor,
        "current_category": flt["category"],
        "keyword": flt["q"],
        "sort_options": SORTS,
        "current_sort": flt["sort"],
        "min_price": flt["min_price"],
        "max_price": flt["max_price"],
        "filters_active": filters_active,
        "filter_summary": " · ".join(summary),
        "show_highlights": show_highlights,
        "bestsellers": bestsellers,
        "newest": newest,
        "testimonials": testimonials,
    })


def detail(request, slug):
    product = get_object_or_404(
        with_ratings(Product.objects.select_related("category")),
        slug=slug, is_available=True,
    )
    related = with_ratings(
        Product.objects.filter(category=product.category, is_available=True)
        .exclude(pk=product.pk)
        .select_related("category")
    )[:4]

    # ----- Đánh giá -----
    reviews = product.reviews.filter(is_visible=True).select_related("user")
    counts = {
        r["rating"]: r["c"]
        for r in product.reviews.filter(is_visible=True).values("rating").annotate(c=Count("id")).order_by()
    }
    total = product.review_count
    breakdown = [
        {"star": s, "count": counts.get(s, 0),
         "percent": round(counts.get(s, 0) * 100 / total) if total else 0}
        for s in (5, 4, 3, 2, 1)
    ]
    bought_user_ids = set(
        _bought_items(product).exclude(order__user=None).values_list("order__user_id", flat=True)
    )

    can_review, review_block = review_permission(request.user, product)
    my_review = None
    if request.user.is_authenticated:
        my_review = Review.objects.filter(product=product, user=request.user).first()

    return render(request, "products/detail.html", {
        "product": product,
        "related": related,
        "reviews": reviews,
        "breakdown": breakdown,
        "bought_user_ids": bought_user_ids,
        "can_review": can_review,
        "review_block": review_block,
        "my_review": my_review,
        "review_form": ReviewForm(instance=my_review),
    })


@require_POST
def review_submit(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    if not request.user.is_authenticated:
        return redirect_to_login(product.get_absolute_url(), resolve_url("accounts:login"))

    allowed, _ = review_permission(request.user, product)
    if not allowed:
        messages.error(request, "Bạn cần mua sản phẩm này trước khi đánh giá.")
        return redirect(product.get_absolute_url())

    existing = Review.objects.filter(product=product, user=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.info(request, "Cảm ơn bạn đã đánh giá!")
        return redirect(f"{product.get_absolute_url()}#reviews")

    errors = []
    if "rating" in form.errors:
        errors.append("Vui lòng chọn số sao (từ 1 đến 5).")
    if "comment" in form.errors:
        errors.append("Nhận xét tối đa 1000 ký tự.")
    messages.error(request, " ".join(errors) or "Đánh giá chưa hợp lệ.")
    return redirect(product.get_absolute_url())


@require_POST
def review_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if not request.user.is_authenticated:
        return redirect_to_login(product.get_absolute_url(), resolve_url("accounts:login"))
    Review.objects.filter(product=product, user=request.user).delete()
    messages.info(request, "Đã xóa đánh giá của bạn.")
    return redirect(f"{product.get_absolute_url()}#reviews")
