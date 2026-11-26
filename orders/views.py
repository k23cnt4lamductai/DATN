from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from products.models import Product

from .cart import Cart
from .forms import CheckoutForm
from .models import Coupon, Order, OrderItem


class StockError(Exception):
    """Hết hàng / không đủ hàng khi đặt."""


class CouponError(Exception):
    """Mã giảm giá không còn dùng được lúc đặt hàng."""


COUPON_SESSION_KEY = "coupon_code"


def _to_int(value, default=1):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _cart_summary(cart):
    items = list(cart)
    total = sum(item["subtotal"] for item in items)
    return items, total


def _pricing(request, subtotal):
    """Áp mã giảm giá đang lưu trong session (nếu còn hợp lệ). Trả về (coupon, giảm giá, phải trả)."""
    code = request.session.get(COUPON_SESSION_KEY)
    if not code:
        return None, 0, subtotal
    coupon = Coupon.objects.filter(code=code).first()
    if coupon is None:
        discount, error = 0, "Mã giảm giá không tồn tại."
    else:
        discount, error = coupon.apply_to(subtotal)
    if error:
        request.session.pop(COUPON_SESSION_KEY, None)
        messages.warning(request, error)
        return None, 0, subtotal
    return coupon, discount, subtotal - discount


# ---------------------------------------------------------------- Giỏ hàng
def cart_detail(request):
    items, total = _cart_summary(Cart(request))
    coupon, discount, final_total = _pricing(request, total) if items else (None, 0, total)
    return render(request, "orders/cart.html", {
        "items": items, "total": total,
        "coupon": coupon, "discount": discount, "final_total": final_total,
    })


@require_POST
def coupon_apply(request):
    code = (request.POST.get("code") or "").strip().upper()
    _, subtotal = _cart_summary(Cart(request))
    if not code:
        messages.error(request, "Vui lòng nhập mã giảm giá.")
    else:
        coupon = Coupon.objects.filter(code=code).first()
        if coupon is None:
            messages.error(request, "Mã giảm giá không tồn tại.")
        else:
            _, error = coupon.apply_to(subtotal)
            if error:
                messages.error(request, error)
            else:
                request.session[COUPON_SESSION_KEY] = coupon.code
                messages.success(request, f"Đã áp dụng mã {coupon.code}.")
    return redirect("orders:cart")


@require_POST
def coupon_remove(request):
    request.session.pop(COUPON_SESSION_KEY, None)
    messages.info(request, "Đã bỏ mã giảm giá.")
    return redirect("orders:cart")


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    quantity = max(_to_int(request.POST.get("quantity")), 1)
    cart = Cart(request)

    if product.stock <= 0:
        messages.error(request, f"{product.name} đã hết hàng.")
    else:
        wanted = cart.quantity_of(product.id) + quantity
        if wanted > product.stock:
            cart.set_quantity(product.id, product.stock)
            messages.warning(
                request,
                f"Trong kho chỉ còn {product.stock} {product.name}, giỏ hàng đã được cập nhật.",
            )
        else:
            cart.set_quantity(product.id, wanted)
            messages.success(request, f"Đã thêm {quantity} × {product.name} vào giỏ hàng.", extra_tags="cart")

    if "buy_now" in request.POST and product.stock > 0:
        return redirect("orders:cart")

    next_url = request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect("orders:cart")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    quantity = _to_int(request.POST.get("quantity"), default=0)
    cart = Cart(request)

    if quantity <= 0:
        cart.remove(product.id)
        messages.info(request, f"Đã xóa {product.name} khỏi giỏ hàng.")
    elif quantity > product.stock:
        cart.set_quantity(product.id, product.stock)
        messages.warning(request, f"Trong kho chỉ còn {product.stock} {product.name}.")
    else:
        cart.set_quantity(product.id, quantity)
        messages.info(request, "Đã cập nhật giỏ hàng.")
    return redirect("orders:cart")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    messages.info(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect("orders:cart")


# ---------------------------------------------------------------- Đặt hàng
def checkout(request):
    cart = Cart(request)
    items, total = _cart_summary(cart)
    if not items:
        messages.info(request, "Giỏ hàng đang trống, hãy chọn vài chiếc bánh nhé.")
        return redirect("orders:cart")
    coupon, discount, final_total = _pricing(request, total)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    order.total = 0
                    order.save()

                    grand_total = 0
                    for item in items:
                        # Khóa dòng sản phẩm để tránh 2 người mua cùng lúc làm âm kho
                        product = Product.objects.select_for_update().get(pk=item["product"].pk)
                        quantity = item["quantity"]
                        if not product.is_available or quantity > product.stock:
                            raise StockError(product.name)

                        OrderItem.objects.create(
                            order=order, product=product,
                            product_name=product.name,
                            price=product.price, quantity=quantity,
                        )
                        product.stock -= quantity
                        product.save(update_fields=["stock", "updated_at"])
                        grand_total += product.price * quantity

                    discount = 0
                    code = request.session.get(COUPON_SESSION_KEY)
                    if code:
                        # Khóa dòng mã giảm giá để 2 đơn cùng lúc không vượt quá số lượt dùng
                        applied = Coupon.objects.select_for_update().filter(code=code).first()
                        error = "Mã giảm giá không tồn tại."
                        if applied:
                            discount, error = applied.apply_to(grand_total)
                        if error:
                            raise CouponError(error)
                        applied.used_count += 1
                        applied.save(update_fields=["used_count"])
                        order.coupon_code = applied.code

                    order.discount = discount
                    order.total = grand_total - discount
                    order.save(update_fields=["total", "discount", "coupon_code", "updated_at"])
            except CouponError as exc:
                request.session.pop(COUPON_SESSION_KEY, None)
                messages.error(request, f"{exc} Đơn hàng chưa được đặt, vui lòng kiểm tra lại.")
                return redirect("orders:cart")
            except StockError as exc:
                messages.error(
                    request,
                    f"Rất tiếc, {exc} không còn đủ hàng. Vui lòng kiểm tra lại giỏ hàng.",
                )
                return redirect("orders:cart")

            cart.clear()
            request.session.pop(COUPON_SESSION_KEY, None)
            request.session["last_order_id"] = order.id
            return redirect("orders:success")
    else:
        initial = {}
        if request.user.is_authenticated:
            last = Order.objects.filter(user=request.user).first()  # đơn gần nhất
            initial["full_name"] = request.user.get_full_name() or (last.full_name if last else "")
            initial["email"] = request.user.email
            saved = getattr(request.user, "profile", None)   # thông tin lưu ở trang cá nhân
            initial["phone"] = (saved.phone if saved else "") or (last.phone if last else "")
            initial["address"] = (saved.address if saved else "") or (last.address if last else "")
        form = CheckoutForm(initial=initial)

    return render(request, "orders/checkout.html", {
        "form": form, "items": items, "total": total,
        "coupon": coupon, "discount": discount, "final_total": final_total,
    })


def order_success(request):
    order_id = request.session.get("last_order_id")
    if not order_id:
        return redirect("products:home")
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "orders/success.html", {
        "order": order, "items": order.items.all(),
    })
