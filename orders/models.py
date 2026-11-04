from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Chờ xác nhận"
        CONFIRMED = "confirmed", "Đã xác nhận"
        DELIVERING = "delivering", "Đang giao"
        COMPLETED = "completed", "Hoàn thành"
        CANCELLED = "cancelled", "Đã hủy"

    class PaymentMethod(models.TextChoices):
        COD = "cod", "Thanh toán khi nhận hàng"
        BANK = "bank", "Chuyển khoản"

    # Khách có thể đặt hàng không cần đăng nhập -> user cho phép null
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="orders", verbose_name="Tài khoản",
    )
    full_name = models.CharField("Họ tên người nhận", max_length=150)
    phone = models.CharField("Số điện thoại", max_length=20)
    email = models.EmailField("Email", blank=True)
    address = models.CharField("Địa chỉ giao hàng", max_length=255)
    note = models.TextField("Ghi chú", blank=True)
    delivery_date = models.DateField("Ngày muốn nhận", null=True, blank=True)

    payment_method = models.CharField(
        "Thanh toán", max_length=10,
        choices=PaymentMethod.choices, default=PaymentMethod.COD,
    )
    status = models.CharField(
        "Trạng thái", max_length=12,
        choices=Status.choices, default=Status.PENDING,
    )
    total = models.DecimalField("Tổng tiền (VNĐ)", max_digits=12, decimal_places=0, default=0)

    created_at = models.DateTimeField("Ngày đặt", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ["-created_at"]

    def recalculate_total(self):
        self.total = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=["total", "updated_at"])

    def __str__(self):
        return f"Đơn #{self.pk} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="items", verbose_name="Đơn hàng",
    )
    # Giữ lại tên + giá tại thời điểm mua, kể cả khi sản phẩm bị sửa/xóa sau này
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="order_items", verbose_name="Sản phẩm",
    )
    product_name = models.CharField("Tên bánh", max_length=200)
    price = models.DecimalField("Đơn giá (VNĐ)", max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField("Số lượng", default=1)

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"

    @property
    def subtotal(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if self.product_id:
            if not self.product_name:
                self.product_name = self.product.name
            if not self.price:
                self.price = self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
