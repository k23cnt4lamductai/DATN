from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from products.models import Product

from .cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem


class StockError(Exception):
    """Hết hàng / không đủ hàng khi đặt."""


def _to_int(value, default=1):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _cart_summary(cart):
    items = list(cart)
    total = sum(item["subtotal"] for item in items)
    return items, total


# ---------------------------------------------------------------- Giỏ hàng
def cart_detail(request):
    items, total = _cart_summary(Cart(request))
    return render(request, "orders/cart.html", {"items": items, "total": total})


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
            messages.success(request, f"Đã thêm {quantity} × {product.name} vào giỏ hàng.")

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

                    order.total = grand_total
                    order.save(update_fields=["total", "updated_at"])
            except StockError as exc:
                messages.error(
                    request,
                    f"Rất tiếc, {exc} không còn đủ hàng. Vui lòng kiểm tra lại giỏ hàng.",
                )
                return redirect("orders:cart")

            cart.clear()
            request.session["last_order_id"] = order.id
            return redirect("orders:success")
    else:
        initial = {}
        if request.user.is_authenticated:
            last = Order.objects.filter(user=request.user).first()  # đơn gần nhất
            initial["full_name"] = request.user.get_full_name() or (last.full_name if last else "")
            initial["email"] = request.user.email
            if last:
                initial["phone"] = last.phone
                initial["address"] = last.address
        form = CheckoutForm(initial=initial)

    return render(request, "orders/checkout.html", {
        "form": form, "items": items, "total": total,
    })


def order_success(request):
    order_id = request.session.get("last_order_id")
    if not order_id:
        return redirect("products:home")
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "orders/success.html", {
        "order": order, "items": order.items.all(),
    })
