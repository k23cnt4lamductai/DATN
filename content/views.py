import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from config.shop_info import SHOP_INFO
from core.templatetags.vnd import vnd
from orders.models import Coupon

from .forms import JobApplicationForm
from .models import Article, JobPosting, Subscriber

NEWS_PAGE_SIZE = 9

logger = logging.getLogger(__name__)

# Mã chào mừng gửi cho người mới đăng ký nhận tin (mỗi người một mã, dùng 1 lần)
WELCOME_VALUE = 20000
WELCOME_MIN_ORDER = 100000
WELCOME_DAYS = 30


def _visible_articles(request):
    """Khách chỉ thấy bài đã đăng; nhân viên quản trị xem được cả bài nháp để xem trước."""
    if request.user.is_authenticated and request.user.is_staff:
        return Article.objects.all()
    return Article.objects.published()


def news_list(request):
    kind = request.GET.get("kind", "")
    if kind not in Article.Kind.values:
        kind = ""
    qs = Article.objects.published()
    if kind:
        qs = qs.filter(kind=kind)
    page = Paginator(qs, NEWS_PAGE_SIZE).get_page(request.GET.get("page"))
    page_numbers = list(page.paginator.get_elided_page_range(page.number, on_each_side=1, on_ends=1))
    return render(request, "content/news_list.html", {
        "page_obj": page,
        "page_numbers": page_numbers,
        "kind": kind,
        "kinds": Article.Kind.choices,
    })


def news_detail(request, slug):
    article = get_object_or_404(_visible_articles(request), slug=slug)
    related = (Article.objects.published().exclude(pk=article.pk)
               .order_by("-published_at")[:3])
    return render(request, "content/news_detail.html", {"article": article, "related": related})


def jobs_list(request):
    jobs = list(JobPosting.objects.filter(is_active=True).select_related("branch"))
    jobs.sort(key=lambda j: not j.is_open)   # còn hạn lên trước, hết hạn xuống cuối
    return render(request, "content/jobs_list.html", {
        "jobs": jobs,
        "open_count": sum(1 for j in jobs if j.is_open),
    })


def job_detail(request, slug):
    qs = JobPosting.objects.select_related("branch")
    if not (request.user.is_authenticated and request.user.is_staff):
        qs = qs.filter(is_active=True)
    job = get_object_or_404(qs, slug=slug)

    if request.method == "POST":
        if not job.is_open:
            messages.error(request, "Vị trí này đã hết hạn nhận hồ sơ.")
            return redirect(job.get_absolute_url())
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            # ?sent=1: trang chi tiết sẽ hiện lời cảm ơn ngay trong khung ứng tuyển
            return redirect(f"{job.get_absolute_url()}?sent=1")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                "full_name": request.user.get_full_name() or request.user.username,
                "email": request.user.email,
            }
        form = JobApplicationForm(initial=initial)

    return render(request, "content/job_detail.html", {
        "job": job, "form": form,
        "sent": request.method == "GET" and request.GET.get("sent") == "1",
    })


@require_POST
def subscribe(request):
    """Đăng ký nhận tin ở chân trang."""
    email = (request.POST.get("email") or "").strip().lower()
    target = request.POST.get("next")
    if not (target and url_has_allowed_host_and_scheme(
            target, allowed_hosts={request.get_host()}, require_https=request.is_secure())):
        target = "/"

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "Email chưa hợp lệ, bạn kiểm tra lại nhé.", extra_tags="newsletter")
        return redirect(f"{target}#newsletter")

    subscriber, created = Subscriber.objects.get_or_create(email=email)
    if created:
        coupon = _new_welcome_coupon()
        try:
            _send_welcome_email(email, coupon)
        except Exception:
            logger.exception("Không gửi được email chào mừng tới %s", email)
            coupon.delete()
            messages.warning(request, "Bạn đã đăng ký thành công nhưng hệ thống chưa gửi được email mã ưu đãi. Vui lòng liên hệ cửa hàng.", extra_tags="newsletter")
        else:
            text = f"Cảm ơn bạn! Mã giảm {vnd(coupon.value)} đã được gửi tới {email}."
            if "console" in settings.EMAIL_BACKEND:
                text += f" (Chế độ thử nghiệm, chưa cấu hình email thật. Mã của bạn: {coupon.code})"
            messages.success(request, text, extra_tags="newsletter")
    elif not subscriber.is_active:
        subscriber.is_active = True
        subscriber.save(update_fields=["is_active"])
        messages.success(request, "Đã bật lại nhận tin cho email này. Cảm ơn bạn!", extra_tags="newsletter")
    else:
        messages.info(request, "Email này đã đăng ký nhận tin rồi.", extra_tags="newsletter")
    return redirect(f"{target}#newsletter")


def _new_welcome_coupon():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = "WELCOME-" + "".join(secrets.choice(alphabet) for _ in range(6))
        if not Coupon.objects.filter(code=code).exists():
            break
    return Coupon.objects.create(
        code=code, description="Mã chào mừng đăng ký nhận tin",
        kind=Coupon.Kind.FIXED, value=WELCOME_VALUE, min_order=WELCOME_MIN_ORDER,
        usage_limit=1, ends_at=timezone.now() + timedelta(days=WELCOME_DAYS),
    )


def _send_welcome_email(email, coupon):
    shop_name = SHOP_INFO.get("name", "Tài Bakery")
    body = (
        f"Cảm ơn bạn đã đăng ký nhận tin từ {shop_name}!\n\n"
        f"Tặng bạn mã giảm {vnd(coupon.value)} cho đơn từ {vnd(coupon.min_order)}:\n\n"
        f"    {coupon.code}\n\n"
        f"Mã dùng được 1 lần, có hiệu lực {WELCOME_DAYS} ngày. "
        f"Nhập mã ở bước Giỏ hàng khi đặt bánh nhé.\n\n"
        f"Hotline: {SHOP_INFO.get('phone', '')}\n{shop_name}"
    )
    send_mail(f"{shop_name} tặng bạn mã giảm giá {vnd(coupon.value)}", body,
              settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
