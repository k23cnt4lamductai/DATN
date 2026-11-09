from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme

from orders.models import Order

from .forms import RegisterForm


def _safe_next(request, value):
    """Chỉ chấp nhận đường dẫn nội bộ để tránh bị chuyển hướng sang web lạ."""
    if value and url_has_allowed_host_and_scheme(
        value, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return value
    return None


class CustomLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("products:home")


def register(request):
    if request.user.is_authenticated:
        return redirect("products:home")

    next_url = request.POST.get("next") or request.GET.get("next") or ""

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # đăng nhập luôn sau khi đăng ký (giỏ hàng vẫn giữ nguyên)
            messages.info(request, f"Chào mừng {user.first_name}! Tài khoản của bạn đã được tạo.")
            return redirect(_safe_next(request, next_url) or "products:home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form, "next": next_url})


@login_required(login_url="accounts:login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "accounts/orders.html", {"orders": orders})


@login_required(login_url="accounts:login")
def order_detail(request, pk):
    # Chỉ xem được đơn của chính mình
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "accounts/order_detail.html", {
        "order": order, "items": order.items.all(),
    })
