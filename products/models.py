from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from content.utils import unique_slug


class Category(models.Model):
    name = models.CharField("Tên danh mục", max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Category, self.name, instance=self, max_length=110, fallback="danh-muc")
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
    weight = models.CharField("Trọng lượng", max_length=50, blank=True, help_text="Ví dụ: 75g")
    shelf_life = models.CharField("Hạn sử dụng", max_length=80, blank=True, help_text="Ví dụ: 03 ngày")
    storage = models.CharField("Bảo quản", max_length=150, blank=True, help_text="Ví dụ: Nhiệt độ điều hoà")
    is_available = models.BooleanField("Đang bán", default=True)
    ingredients = models.ManyToManyField(
        "Ingredient", through="ProductIngredient",
        related_name="products", verbose_name="Thành phần", blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Product, self.name, instance=self, max_length=200, fallback="banh")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:detail", args=[self.slug])

    def _ordered_ingredients(self):
        """Thành phần xếp theo định lượng giảm dần (đúng quy ước ghi nhãn); chưa có định lượng thì xếp cuối."""
        rows = list(self.product_ingredients.select_related("ingredient"))
        rows.sort(key=lambda r: (r.quantity is None, -(r.quantity or 0), r.ingredient.name))
        return [r.ingredient for r in rows]

    @property
    def ingredient_text(self):
        """'Bột mì, bơ lạt, trứng gà...' - hiển thị ở khung Thông tin sản phẩm."""
        names = [i.name.split(" (")[0] for i in self._ordered_ingredients()]
        if not names:
            return ""
        return ", ".join([names[0]] + [n[:1].lower() + n[1:] for n in names[1:]])

    @property
    def allergen_text(self):
        names = [i.name.split(" (")[0].lower() for i in self._ordered_ingredients() if i.is_allergen]
        return ", ".join(names)

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

class Ingredient(models.Model):
    """Thành phần / nguyên liệu dùng để làm bánh."""

    class Unit(models.TextChoices):
        GRAM = "g", "gram"
        ML = "ml", "ml"
        PIECE = "pcs", "cái / quả"
        TSP = "tsp", "thìa cà phê"

    name = models.CharField("Tên thành phần", max_length=120, unique=True)
    unit = models.CharField("Đơn vị", max_length=5, choices=Unit.choices, default=Unit.GRAM)
    is_allergen = models.BooleanField("Có thể gây dị ứng", default=False)
    note = models.CharField("Ghi chú", max_length=200, blank=True)

    class Meta:
        verbose_name = "Thành phần"
        verbose_name_plural = "Thành phần"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductIngredient(models.Model):
    """Một bánh dùng những thành phần nào, mỗi loại bao nhiêu."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="product_ingredients", verbose_name="Sản phẩm",
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT,
        related_name="product_ingredients", verbose_name="Thành phần",
    )
    quantity = models.DecimalField("Định lượng", max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Thành phần của bánh"
        verbose_name_plural = "Thành phần của bánh"
        constraints = [
            models.UniqueConstraint(fields=["product", "ingredient"], name="unique_ingredient_per_product"),
        ]

    def __str__(self):
        return f"{self.product} - {self.ingredient}"


class Wishlist(models.Model):
    """Bánh khách đã bấm tim (danh sách yêu thích)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="wishlist_items", verbose_name="Khách hàng",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="wishlisted_by", verbose_name="Sản phẩm",
    )
    created_at = models.DateTimeField("Ngày thêm", auto_now_add=True)

    class Meta:
        verbose_name = "Sản phẩm yêu thích"
        verbose_name_plural = "Sản phẩm yêu thích"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_wishlist_per_user_product"),
        ]

    def __str__(self):
        return f"{self.user} ♥ {self.product}"
