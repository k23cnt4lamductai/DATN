from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.views.decorators.http import require_POST

from orders.models import Order, OrderItem

from .forms import ReviewForm
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


def home(request):
    products = Product.objects.filter(is_available=True).select_related("category")
    categories = Category.objects.all()

    category_slug = request.GET.get("category")
    keyword = request.GET.get("q")

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if keyword:
        products = products.filter(name__icontains=keyword)

    return render(request, "products/home.html", {
        "products": with_ratings(products),
        "categories": categories,
        "current_category": category_slug,
        "keyword": keyword or "",
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
