from django.db import models
from django.urls import reverse
from django.utils import timezone

from .utils import unique_slug


class ArticleQuerySet(models.QuerySet):
    def published(self):
        """Bài đã bật hiển thị và đã đến giờ đăng."""
        return self.filter(is_published=True, published_at__lte=timezone.now())


class Article(models.Model):
    """Bài viết: tin tức hoặc chương trình khuyến mại."""

    class Kind(models.TextChoices):
        NEWS = "news", "Tin tức"
        PROMO = "promo", "Khuyến mại"

    title = models.CharField("Tiêu đề", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True,
                            help_text="Để trống để tự tạo từ tiêu đề.")
    kind = models.CharField("Loại bài", max_length=10, choices=Kind.choices, default=Kind.NEWS)
    summary = models.CharField("Mô tả ngắn", max_length=300, blank=True,
                               help_text="Hiện ở danh sách bài viết.")
    body = models.TextField("Nội dung", help_text="Xuống dòng để tách đoạn.")
    image = models.ImageField("Ảnh đại diện", upload_to="articles/", blank=True)
    is_published = models.BooleanField("Hiển thị trên website", default=True)
    published_at = models.DateTimeField("Ngày đăng", default=timezone.now,
                                        help_text="Đặt ngày trong tương lai để hẹn giờ đăng.")
    promo_ends = models.DateField("Khuyến mại đến hết ngày", null=True, blank=True,
                                  help_text="Chỉ dùng cho bài Khuyến mại. Để trống nếu không giới hạn.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = "Bài viết"
        verbose_name_plural = "Tin tức & Khuyến mại"
        ordering = ["-published_at", "-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Article, self.title, instance=self, max_length=200)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("content:news_detail", args=[self.slug])

    @property
    def is_promo(self):
        return self.kind == self.Kind.PROMO

    @property
    def is_expired(self):
        """Khuyến mại đã quá hạn."""
        return bool(self.is_promo and self.promo_ends and self.promo_ends < timezone.localdate())

    @property
    def list_summary(self):
        """Mô tả ngắn; nếu chưa nhập thì lấy đoạn đầu của nội dung."""
        if self.summary:
            return self.summary
        first = next((p.strip() for p in self.body.splitlines() if p.strip()), "")
        return first


class JobPosting(models.Model):
    """Tin tuyển dụng."""

    class JobType(models.TextChoices):
        FULL = "full", "Toàn thời gian"
        PART = "part", "Bán thời gian"
        INTERN = "intern", "Thực tập"

    title = models.CharField("Vị trí tuyển dụng", max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True,
                            help_text="Để trống để tự tạo từ tên vị trí.")
    branch = models.ForeignKey(
        "stores.Branch", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="jobs", verbose_name="Chi nhánh làm việc",
        help_text="Để trống nếu làm việc tại toàn hệ thống.",
    )
    job_type = models.CharField("Hình thức", max_length=10, choices=JobType.choices, default=JobType.FULL)
    headcount = models.PositiveSmallIntegerField("Số lượng cần tuyển", default=1)
    salary = models.CharField("Mức lương", max_length=100, default="Thỏa thuận")
    description = models.TextField("Mô tả công việc")
    requirements = models.TextField("Yêu cầu", blank=True, help_text="Mỗi dòng một ý.")
    benefits = models.TextField("Quyền lợi", blank=True, help_text="Mỗi dòng một ý.")
    deadline = models.DateField("Hạn nộp hồ sơ", null=True, blank=True)
    is_active = models.BooleanField("Đang tuyển", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tin tuyển dụng"
        verbose_name_plural = "Tin tuyển dụng"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(JobPosting, self.title, instance=self, max_length=150, fallback="tuyen-dung")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("content:job_detail", args=[self.slug])

    @property
    def location(self):
        return self.branch.name if self.branch_id else "Toàn hệ thống"

    @property
    def is_open(self):
        """Còn nhận hồ sơ: đang bật và chưa quá hạn nộp."""
        if not self.is_active:
            return False
        return self.deadline is None or self.deadline >= timezone.localdate()


class JobApplication(models.Model):
    """Hồ sơ ứng tuyển gửi từ website."""

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE,
                            related_name="applications", verbose_name="Vị trí ứng tuyển")
    full_name = models.CharField("Họ và tên", max_length=120)
    phone = models.CharField("Số điện thoại", max_length=20)
    email = models.EmailField("Email")
    message = models.TextField("Giới thiệu bản thân / link CV", blank=True)
    is_handled = models.BooleanField("Đã liên hệ", default=False)
    created_at = models.DateTimeField("Ngày gửi", auto_now_add=True)

    class Meta:
        verbose_name = "Hồ sơ ứng tuyển"
        verbose_name_plural = "Hồ sơ ứng tuyển"
        ordering = ["is_handled", "-created_at"]

    def __str__(self):
        return f"{self.full_name} – {self.job}"


class Subscriber(models.Model):
    """Email khách đăng ký nhận tin khuyến mại."""

    email = models.EmailField("Email", unique=True)
    is_active = models.BooleanField("Đang nhận tin", default=True)
    created_at = models.DateTimeField("Ngày đăng ký", auto_now_add=True)

    class Meta:
        verbose_name = "Người đăng ký nhận tin"
        verbose_name_plural = "Người đăng ký nhận tin"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.email = (self.email or "").strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
