from django.core.management.base import BaseCommand

from products.models import Category, Product

DATA = {
    "Bánh kem": [
        ("Bánh kem dâu tây", "Bánh bông lan mềm, kem tươi và dâu tây Đà Lạt.", 350000, 10),
        ("Bánh kem socola", "Socola đen đậm vị, phủ ganache mịn.", 380000, 8),
        ("Bánh kem trà xanh", "Vị matcha thanh nhẹ, ít ngọt.", 360000, 6),
    ],
    "Bánh mì ngọt": [
        ("Bánh mì bơ sữa", "Mềm xốp, thơm mùi bơ sữa.", 25000, 40),
        ("Bánh mì sữa tươi", "Nhân kem sữa béo ngậy.", 22000, 40),
    ],
    "Bánh cupcake": [
        ("Cupcake vani", "Cupcake vani phủ kem bơ.", 30000, 30),
        ("Cupcake red velvet", "Red velvet với kem phô mai.", 35000, 25),
    ],
    "Bánh quy": [
        ("Cookie socola chip", "Giòn rụm, nhiều socola chip.", 15000, 60),
        ("Macaron hộp 6 cái", "Macaron nhiều vị, đóng hộp quà.", 120000, 15),
    ],
}


class Command(BaseCommand):
    help = "Nạp danh mục & sản phẩm bánh ngọt mẫu (chạy nhiều lần không bị trùng)"

    def handle(self, *args, **options):
        created = 0
        for cat_name, items in DATA.items():
            category, _ = Category.objects.get_or_create(name=cat_name)
            for name, desc, price, stock in items:
                _, is_new = Product.objects.get_or_create(
                    name=name,
                    defaults={"category": category, "description": desc,
                              "price": price, "stock": stock},
                )
                created += is_new
        self.stdout.write(self.style.SUCCESS(f"Xong. Đã thêm {created} sản phẩm mới."))
