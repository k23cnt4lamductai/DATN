"""Thêm đánh giá + nhận xét mẫu cho các sản phẩm (mỗi người chỉ đánh giá một bánh một lần).
Đánh giá nào cũng khớp với dữ liệu khách hàng: người đánh giá phải có đơn hàng (chưa hủy) chứa bánh đó.
Nếu chưa có, lệnh tự tạo một đơn "Hoàn thành" trước ngày đánh giá. Đánh giá cũ thiếu đơn cũng được bổ sung.

Chạy:  python manage.py seed_reviews                 (mỗi bánh có ít nhất 3 đánh giá)
       python manage.py seed_reviews --per-product 6  (mỗi bánh có ít nhất 6 đánh giá)
Chạy lại không bị trùng; bánh đã đủ số đánh giá thì bỏ qua.
"""
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone

from accounts.models import Profile
from orders.models import Order, OrderItem
from products.models import Product, Review

GENERIC = {
    5: [
        "Bánh mềm, ngọt vừa phải, giao đúng giờ. Cả nhà ăn đều khen, chắc chắn sẽ đặt lại.",
        "Đóng gói cẩn thận, bánh còn nguyên vẹn khi nhận. Vị béo nhẹ, không bị ngấy.",
        "Mua làm quà cho bạn, bạn rất thích. Trang trí xinh và hương vị rất ổn.",
        "Nhân viên tư vấn nhiệt tình, bánh tươi ngon. Giá hợp lý so với chất lượng.",
        "Lần thứ hai đặt ở đây, vẫn giữ được chất lượng như lần đầu. Rất đáng thử.",
        "Bánh làm mới trong ngày nên rất tươi, ăn là thấy khác biệt ngay.",
        "Hương vị đậm đà mà không quá ngọt, hợp khẩu vị cả người lớn và trẻ nhỏ.",
        "Đặt buổi sáng, chiều nhận được bánh. Nhanh và đúng như hình, rất hài lòng.",
    ],
    4: [
        "Bánh ngon, vị hơi ngọt với mình nhưng cốt bánh rất mềm. Sẽ giới thiệu bạn bè.",
        "Giao hàng nhanh, bánh tươi. Nếu giảm bớt độ ngọt một chút thì tuyệt vời hơn.",
        "Hương vị ổn, đóng gói đẹp. Mong cửa hàng có thêm nhiều vị mới.",
        "Bánh ngon, giá hợp lý. Lần sau mình sẽ thử thêm các loại khác của tiệm.",
        "Chất lượng tốt, chỉ tiếc là phần trang trí hơi đơn giản so với mong đợi.",
        "Ăn vừa miệng, giao đúng hẹn. Cho 4 sao vì mình mong phần bánh to hơn một chút.",
    ],
    3: [
        "Bánh ăn ổn, không có gì đặc biệt lắm nhưng giao hàng đúng giờ.",
        "Vị hơi ngọt so với khẩu vị của mình, nhưng đóng gói cẩn thận.",
        "Bánh tạm được, mong lần sau cửa hàng điều chỉnh độ ngọt nhẹ hơn.",
    ],
}

BY_KIND = {
    "kem": {
        5: [
            "Bánh kem mềm xốp, lớp kem mịn và béo nhẹ, không bị ngấy. Dùng cho sinh nhật rất hợp.",
            "Cốt bánh ẩm, kem tươi thơm. Cả nhà chia nhau hết sạch trong buổi tối.",
            "Bánh kem trang trí đẹp, cắt ra các lớp rất đều. Mọi người đều khen ngon.",
        ],
        4: ["Bánh kem ngon, kem hơi nhiều với mình nhưng cốt bánh rất mềm."],
    },
    "mì": {
        5: [
            "Bánh mì mềm, thơm bơ sữa, ăn sáng cùng cà phê là hết ý.",
            "Ruột bánh mềm xốp, nhân vừa ăn, để qua ngày vẫn không bị khô.",
        ],
        4: ["Bánh mì ngon, nhân hơi ít một chút nhưng vỏ bánh rất thơm."],
    },
    "cupcake": {
        5: [
            "Cupcake nhỏ xinh, kem bơ mịn, cốt bánh ẩm. Mua tặng bạn bè ai cũng thích.",
            "Trang trí đẹp mắt, vị cân bằng, ăn một cái là muốn thêm cái nữa.",
        ],
        4: ["Cupcake ngon, kem hơi ngọt một chút nhưng nhìn rất xinh."],
    },
    "quy": {
        5: [
            "Cookie giòn ngoài mềm trong, thơm bơ, ăn kèm trà rất hợp.",
            "Bánh quy giòn tan, không quá ngọt. Mua thêm để dành ăn dần.",
        ],
        4: ["Bánh quy thơm, giòn đều. Mong có thêm hộp quà để tặng."],
    },
}


def kind_of(product):
    text = f"{product.category.name} {product.name}".lower()
    for key in ("cupcake", "quy", "cookie", "mì", "kem"):
        if key in text:
            return {"cookie": "quy"}.get(key, key)
    return None


def ensure_purchase(user, product, review_time, rng, counters):
    """Đảm bảo user có đơn chưa hủy chứa bánh này (tạo đơn Hoàn thành trước ngày đánh giá nếu thiếu)."""
    bought = OrderItem.objects.filter(product=product, order__user=user).exclude(
        order__status=Order.Status.CANCELLED)
    if bought.exists():
        return
    profile, _ = Profile.objects.get_or_create(user=user)
    qty = rng.choice([1, 1, 2])
    when = review_time - timedelta(days=rng.randint(2, 6), hours=rng.randint(0, 10))
    order = Order.objects.create(
        user=user, full_name=user.get_full_name() or user.get_username(),
        phone=profile.phone or "0912345678", email=user.email,
        address=profile.address or "Hà Nội", delivery_date=when.date(),
        payment_method=rng.choice([Order.PaymentMethod.COD, Order.PaymentMethod.BANK]),
        status=Order.Status.COMPLETED, total=product.price * qty, is_paid=True,
    )
    Order.objects.filter(pk=order.pk).update(created_at=when)
    OrderItem.objects.create(order=order, product=product, product_name=product.name,
                             price=product.price, quantity=qty)
    Product.objects.filter(pk=product.pk, stock__gte=qty).update(stock=F("stock") - qty)
    counters["orders"] += 1


class Command(BaseCommand):
    help = "Thêm đánh giá và nhận xét mẫu cho sản phẩm (chạy nhiều lần không bị trùng)"

    def add_arguments(self, parser):
        parser.add_argument("--per-product", type=int, default=3,
                            help="Số đánh giá tối thiểu cho mỗi bánh (mặc định 3)")

    def handle(self, *args, **options):
        target = options["per_product"]
        rng = random.Random(7)
        User = get_user_model()
        users = list(User.objects.filter(is_staff=False, is_superuser=False))
        if not users:
            self.stderr.write("Chưa có tài khoản khách. Hãy chạy seed_extra / seed_orders trước.")
            return
        now = timezone.now()
        added = 0
        counters = {"orders": 0}

        # Bước 1: đánh giá đã có mà người viết chưa từng mua bánh đó -> bổ sung đơn hàng cho khớp
        for review in Review.objects.select_related("user", "product"):
            ensure_purchase(review.user, review.product, review.created_at, rng, counters)

        for product in Product.objects.filter(is_available=True).select_related("category"):
            have = Review.objects.filter(product=product)
            need = target - have.count()
            if need <= 0:
                continue
            reviewed = set(have.values_list("user_id", flat=True))
            buyers = set(
                OrderItem.objects.filter(product=product).exclude(order__status="cancelled")
                .exclude(order__user=None).values_list("order__user_id", flat=True)
            )
            pool = [u for u in users if u.pk not in reviewed]
            rng.shuffle(pool)
            pool.sort(key=lambda u: u.pk not in buyers)          # người đã mua xếp trước
            kind = kind_of(product)
            used = set(have.values_list("comment", flat=True))

            for user in pool[:need]:
                stars = rng.choices([5, 4, 3], weights=[58, 34, 8])[0]
                options_ = GENERIC[stars] + BY_KIND.get(kind, {}).get(stars, []) * 2
                options_ = [c for c in options_ if c not in used] or GENERIC[stars]
                comment = rng.choice(options_)
                used.add(comment)
                when = now - timedelta(days=rng.randint(0, 20), hours=rng.randint(0, 20))
                ensure_purchase(user, product, when, rng, counters)
                review = Review.objects.create(product=product, user=user, rating=stars, comment=comment)
                Review.objects.filter(pk=review.pk).update(created_at=when)
                added += 1

        self.stdout.write(self.style.SUCCESS(f"Xong. Đã thêm {added} đánh giá mới."))
        if counters["orders"]:
            self.stdout.write(f"Đã tạo thêm {counters['orders']} đơn hàng 'Hoàn thành' để mỗi người đánh giá đều có đơn mua bánh đó.")
        self.stdout.write("Xem ở trang chủ (mục Khách hàng nói gì), trang chi tiết bánh và admin > Đánh giá.")
