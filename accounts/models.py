from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Thông tin cá nhân thêm cho tài khoản (số điện thoại, địa chỉ, ngày sinh)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="profile", verbose_name="Tài khoản",
    )
    phone = models.CharField("Số điện thoại", max_length=20, blank=True)
    address = models.CharField("Địa chỉ giao hàng mặc định", max_length=255, blank=True)
    birth_date = models.DateField("Ngày sinh", null=True, blank=True)

    class Meta:
        verbose_name = "Thông tin cá nhân"
        verbose_name_plural = "Thông tin cá nhân"

    def __str__(self):
        return f"Hồ sơ của {self.user}"


def get_profile(user):
    """Lấy hồ sơ của tài khoản, chưa có thì tạo (tài khoản cũ không bị lỗi)."""
    return Profile.objects.get_or_create(user=user)[0]
