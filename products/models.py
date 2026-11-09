from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("Tên danh mục", max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name="products", verbose_name="Danh mục",
    )
    name = models.CharField("Tên bánh", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField("Mô tả", blank=True)
    price = models.DecimalField("Giá (VNĐ)", max_digits=10, decimal_places=0)
    image = models.ImageField("Hình ảnh", upload_to="products/", blank=True)
    stock = models.PositiveIntegerField("Số lượng tồn", default=0)
    is_available = models.BooleanField("Đang bán", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:detail", args=[self.slug])

    def __str__(self):
        return self.name


class Review(models.Model):
    """Đánh giá (1-5 sao) + nhận xét của khách cho một sản phẩm. Mỗi người chỉ đánh giá 1 lần / sản phẩm."""

    RATING_CHOICES = [(i, f"{i} sao") for i in range(5, 0, -1)]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="reviews", verbose_name="Sản phẩm",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="reviews", verbose_name="Người đánh giá",
    )
    rating = models.PositiveSmallIntegerField(
        "Số sao", choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("Nhận xét", blank=True, max_length=1000)
    is_visible = models.BooleanField("Hiển thị", default=True)
    created_at = models.DateTimeField("Ngày đánh giá", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["product", "user"], name="unique_review_per_user_product"),
        ]

    def __str__(self):
        return f"{self.product} - {self.user} - {self.rating} sao"
