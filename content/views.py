from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import JobApplicationForm
from .models import Article, JobPosting

NEWS_PAGE_SIZE = 9


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
