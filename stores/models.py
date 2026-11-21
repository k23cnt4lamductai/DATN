from django.db import models


class Branch(models.Model):
    """Chi nhánh cửa hàng Tài Bakery."""

    name = models.CharField("Tên chi nhánh", max_length=150, unique=True)
    address = models.CharField("Địa chỉ", max_length=255)
    district = models.CharField("Quận / huyện", max_length=100, blank=True)
    city = models.CharField("Thành phố", max_length=100, default="Hà Nội")
    phone = models.CharField("Số điện thoại", max_length=20, blank=True)
    open_time = models.TimeField("Giờ mở cửa", default="07:00")
    close_time = models.TimeField("Giờ đóng cửa", default="21:30")
    is_active = models.BooleanField("Đang hoạt động", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chi nhánh"
        verbose_name_plural = "Chi nhánh"
        ordering = ["name"]

    def __str__(self):
        return self.name
