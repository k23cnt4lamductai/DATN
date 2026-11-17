from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F

from products.models import Product

from .stock_rules import stock_action


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Trạng thái lúc đọc từ CSDL: để biết khi nào đơn bị hủy / được khôi phục
        self._loaded_status = self.__dict__.get("status")

    def recalculate_total(self):
        self.total = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=["total", "updated_at"])

    # ---------- Tồn kho theo trạng thái đơn ----------
    def _items_with_product(self):
        return self.items.select_related("product").exclude(product=None)

    def _restore_problem(self):
        """Tên bánh không đủ tồn kho để khôi phục đơn đã hủy (None nếu ổn)."""
        if self._state.adding or stock_action(self._loaded_status, self.status) != "deduct":
            return None
        for item in self._items_with_product():
            if item.product.stock < item.quantity:
                return item.product_name
        return None

    def clean(self):
        super().clean()
        name = self._restore_problem()
        if name:
            raise ValidationError(f"Không thể khôi phục đơn: “{name}” không đủ tồn kho.")

    def _adjust_stock(self, restore):
        for item in self._items_with_product():
            products = Product.objects.filter(pk=item.product_id)
            if restore:
                products.update(stock=F("stock") + item.quantity)
            elif not products.filter(stock__gte=item.quantity).update(stock=F("stock") - item.quantity):
                raise ValidationError(f"Không thể khôi phục đơn: “{item.product_name}” không đủ tồn kho.")

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        action = None
        if not self._state.adding and (update_fields is None or "status" in update_fields):
            action = stock_action(self._loaded_status, self.status)
        with transaction.atomic():
            super().save(*args, **kwargs)
            if action:
                self._adjust_stock(restore=(action == "restore"))
        self._loaded_status = self.status

    def change_status(self, new_status):
        """Đổi trạng thái (tự hoàn / trừ tồn kho). Ném ValidationError nếu không làm được."""
        if new_status not in self.Status.values:
            raise ValidationError("Trạng thái không hợp lệ.")
        if new_status == self.status:
            return
        old = self.status
        self.status = new_status
        try:
            self.clean()
            self.save()
        except ValidationError:
            self.status = old
            raise

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
