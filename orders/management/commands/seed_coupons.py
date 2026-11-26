"""Tạo vài mã giảm giá mẫu:  python manage.py seed_coupons  (chạy lại không bị trùng)"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Coupon


class Command(BaseCommand):
    help = "Tạo mã giảm giá mẫu (TAI10, CHAOBAN, QUA50)"

    def handle(self, *args, **options):
        now = timezone.now()
        samples = [
            dict(code="TAI10", description="Giảm 10% cho đơn từ 150.000đ (tối đa 50.000đ)",
                 kind=Coupon.Kind.PERCENT, value=10, min_order=150000, max_discount=50000,
                 ends_at=now + timedelta(days=90)),
            dict(code="CHAOBAN", description="Giảm 20.000đ cho đơn từ 100.000đ",
                 kind=Coupon.Kind.FIXED, value=20000, min_order=100000),
            dict(code="QUA50", description="Giảm 50.000đ cho đơn từ 300.000đ, 20 lượt đầu",
                 kind=Coupon.Kind.FIXED, value=50000, min_order=300000, usage_limit=20),
        ]
        created = 0
        for data in samples:
            code = data.pop("code")
            _, new = Coupon.objects.get_or_create(code=code, defaults=data)
            created += new
        self.stdout.write(self.style.SUCCESS(f"Xong. Đã thêm {created} mã giảm giá mới."))
        self.stdout.write("Xem và sửa mã trong trang quản trị, mục Mã giảm giá.")
