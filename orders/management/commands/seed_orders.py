"""Tạo đơn hàng, đánh giá và danh sách yêu thích mẫu cho những khách chưa có đơn nào,
rồi đặt mật khẩu mẫu để bạn đăng nhập thử bằng từng tài khoản.

Chạy:  python manage.py seed_orders
Chạy lại nhiều lần không tạo thêm (chỉ xử lý khách chưa có đơn).
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone

from accounts.models import Profile
from orders.models import Coupon, Order, OrderItem
from products.models import Product, Review, Wishlist

DEMO_PASSWORD = "Taibakery@123"

ADDRESSES = [
    "12 Nguyễn Chí Thanh, Láng Thượng, Đống Đa, Hà Nội",
    "45 Trần Duy Hưng, Trung Hòa, Cầu Giấy, Hà Nội",
    "88 Lê Văn Lương, Nhân Chính, Thanh Xuân, Hà Nội",
    "27 Hoàng Quốc Việt, Nghĩa Tân, Cầu Giấy, Hà Nội",
    "103 Kim Mã, Ngọc Khánh, Ba Đình, Hà Nội",
    "9 Phạm Hùng, Mễ Trì, Nam Từ Liêm, Hà Nội",
    "56 Xuân Thủy, Dịch Vọng Hậu, Cầu Giấy, Hà Nội",
    "21 Nguyễn Trãi, Thượng Đình, Thanh Xuân, Hà Nội",
    "70 Giải Phóng, Phương Mai, Đống Đa, Hà Nội",
    "34 Tây Sơn, Quang Trung, Đống Đa, Hà Nội",
]

COMMENTS_5 = [
    "Bánh mềm, ngọt vừa phải, giao đúng giờ. Cả nhà ăn đều khen, chắc chắn sẽ đặt lại.",
    "Đóng gói cẩn thận, bánh còn nguyên vẹn khi nhận. Vị béo nhẹ, không bị ngấy.",
    "Mua làm quà sinh nhật cho bạn, bạn rất thích. Trang trí xinh và hương vị rất ổn.",
    "Nhân viên tư vấn nhiệt tình, bánh tươi ngon. Giá hợp lý so với chất lượng.",
    "Lần thứ hai đặt ở đây, vẫn giữ được chất lượng như lần đầu. Rất đáng thử.",
]
COMMENTS_4 = [
    "Bánh ngon, vị hơi ngọt với mình nhưng cốt bánh rất mềm. Sẽ giới thiệu bạn bè.",
    "Giao hàng nhanh, bánh tươi. Nếu giảm bớt độ ngọt một chút thì tuyệt vời hơn.",
    "Hương vị ổn, đóng gói đẹp. Mong cửa hàng có thêm nhiều vị mới.",
]


class Command(BaseCommand):
    help = "Tạo đơn hàng / đánh giá / yêu thích mẫu cho khách chưa có đơn và in danh sách tài khoản đăng nhập thử"

    def handle(self, *args, **options):
        rng = random.Random(2026)
        User = get_user_model()
        products = list(Product.objects.filter(is_available=True, stock__gt=0))
        if not products:
            self.stderr.write("Chưa có sản phẩm. Hãy chạy seed_data / seed_more trước.")
            return
        chaoban = Coupon.objects.filter(code="CHAOBAN", is_active=True).first()
        now = timezone.now()

        customers = [u for u in User.objects.filter(is_staff=False, is_superuser=False).order_by("pk")
                     if not u.orders.exists()]
        n_orders = n_reviews = 0

        for user in customers:
            name = user.get_full_name() or user.get_username()
            profile, _ = Profile.objects.get_or_create(user=user)
            if not profile.phone:
                profile.phone = "09" + "".join(str(rng.randint(0, 9)) for _ in range(8))
            if not profile.address:
                profile.address = rng.choice(ADDRESSES)
            profile.save()
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=["password"])

            for _ in range(rng.choice([1, 2, 2, 3])):
                status = rng.choices(
                    [Order.Status.COMPLETED, Order.Status.DELIVERING, Order.Status.CONFIRMED,
                     Order.Status.PENDING, Order.Status.CANCELLED],
                    weights=[60, 8, 8, 8, 6])[0]
                chosen = rng.sample(products, rng.choice([1, 2, 2, 3]))
                lines = [(p, rng.choice([1, 1, 2, 3])) for p in chosen]
                subtotal = sum(p.price * q for p, q in lines)
                discount, code = Decimal(0), ""
                if chaoban and subtotal >= chaoban.min_order and rng.random() < 0.3:
                    discount, code = Decimal(chaoban.value), chaoban.code
                    Coupon.objects.filter(pk=chaoban.pk).update(used_count=F("used_count") + 1)

                bank = rng.random() < 0.4
                when = now - timedelta(days=rng.randint(0, 24), hours=rng.randint(0, 20))
                order = Order.objects.create(
                    user=user, full_name=name, phone=profile.phone, email=user.email,
                    address=profile.address, delivery_date=when.date(),
                    payment_method=Order.PaymentMethod.BANK if bank else Order.PaymentMethod.COD,
                    status=status, total=subtotal - discount, discount=discount, coupon_code=code,
                    is_paid=(status == Order.Status.COMPLETED),
                )
                Order.objects.filter(pk=order.pk).update(created_at=when)
                for p, q in lines:
                    OrderItem.objects.create(order=order, product=p, product_name=p.name, price=p.price, quantity=q)
                    if status != Order.Status.CANCELLED:        # đơn chưa hủy thì đã trừ kho
                        Product.objects.filter(pk=p.pk, stock__gte=q).update(stock=F("stock") - q)
                n_orders += 1

                if status == Order.Status.COMPLETED and rng.random() < 0.6:
                    p = rng.choice(lines)[0]
                    stars = rng.choices([5, 4], weights=[70, 30])[0]
                    comment = rng.choice(COMMENTS_5 if stars == 5 else COMMENTS_4)
                    _, new = Review.objects.get_or_create(
                        user=user, product=p, defaults={"rating": stars, "comment": comment})
                    n_reviews += new

            for p in rng.sample(products, rng.choice([2, 3, 4])):
                Wishlist.objects.get_or_create(user=user, product=p)

        self.stdout.write(self.style.SUCCESS(
            f"Xong. Xử lý {len(customers)} khách, tạo {n_orders} đơn hàng và {n_reviews} đánh giá."))

        # Danh sách tài khoản đăng nhập thử (mật khẩu mẫu)
        self.stdout.write("\nTÀI KHOẢN ĐĂNG NHẬP THỬ (mật khẩu: %s)" % DEMO_PASSWORD)
        self.stdout.write("%-22s %s" % ("Tên đăng nhập", "Họ tên / Email"))
        for u in User.objects.filter(is_staff=False, is_superuser=False).order_by("pk"):
            if u.check_password(DEMO_PASSWORD):
                self.stdout.write("%-22s %s  <%s>" % (u.get_username(), u.get_full_name(), u.email))
