from datetime import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Ingredient, Product, ProductIngredient
from stores.models import Branch

U = Ingredient.Unit

# (tên, đơn vị, có thể gây dị ứng, ghi chú)
INGREDIENTS = [
    ("Bột mì", U.GRAM, True, "Chứa gluten"),
    ("Bột bắp", U.GRAM, False, ""),
    ("Đường", U.GRAM, False, ""),
    ("Đường bột", U.GRAM, False, ""),
    ("Muối", U.GRAM, False, ""),
    ("Men nở", U.GRAM, False, ""),
    ("Bột nở", U.GRAM, False, ""),
    ("Trứng gà", U.PIECE, True, ""),
    ("Sữa tươi", U.ML, True, "Chứa lactose"),
    ("Bơ lạt", U.GRAM, True, ""),
    ("Kem tươi (whipping cream)", U.ML, True, ""),
    ("Phô mai kem (cream cheese)", U.GRAM, True, ""),
    ("Socola đen", U.GRAM, True, "Có thể chứa sữa, đậu nành"),
    ("Bột cacao", U.GRAM, False, ""),
    ("Bột trà xanh matcha", U.GRAM, False, ""),
    ("Dâu tây", U.GRAM, False, ""),
    ("Hạnh nhân bột", U.GRAM, True, "Hạt cây"),
    ("Vani", U.TSP, False, ""),
    ("Màu thực phẩm đỏ", U.TSP, False, ""),
    ("Dầu ăn", U.ML, False, ""),
]

# tên bánh -> [(thành phần, định lượng cho 1 bánh / 1 phần)]
RECIPES = {
    "Bánh kem dâu tây": [("Bột mì", 120), ("Trứng gà", 4), ("Đường", 100), ("Sữa tươi", 60),
                         ("Kem tươi (whipping cream)", 300), ("Dâu tây", 250), ("Vani", 1)],
    "Bánh kem socola": [("Bột mì", 110), ("Bột cacao", 30), ("Trứng gà", 4), ("Đường", 110),
                        ("Socola đen", 200), ("Kem tươi (whipping cream)", 250), ("Bơ lạt", 50)],
    "Bánh kem trà xanh": [("Bột mì", 120), ("Bột trà xanh matcha", 12), ("Trứng gà", 4), ("Đường", 100),
                          ("Sữa tươi", 60), ("Kem tươi (whipping cream)", 300)],
    "Bánh mì bơ sữa": [("Bột mì", 60), ("Bơ lạt", 8), ("Sữa tươi", 25), ("Đường", 6),
                       ("Men nở", 1), ("Trứng gà", 1), ("Muối", 1)],
    "Bánh mì sữa tươi": [("Bột mì", 55), ("Sữa tươi", 35), ("Đường", 7), ("Men nở", 1),
                         ("Kem tươi (whipping cream)", 15), ("Muối", 1)],
    "Cupcake vani": [("Bột mì", 35), ("Bơ lạt", 25), ("Đường", 30), ("Trứng gà", 1),
                     ("Sữa tươi", 20), ("Vani", 1), ("Bột nở", 1)],
    "Cupcake red velvet": [("Bột mì", 35), ("Bột cacao", 3), ("Bơ lạt", 20), ("Đường", 30), ("Trứng gà", 1),
                           ("Phô mai kem (cream cheese)", 25), ("Màu thực phẩm đỏ", 1)],
    "Cookie socola chip": [("Bột mì", 30), ("Bơ lạt", 20), ("Đường", 15), ("Trứng gà", 1), ("Socola đen", 15)],
    "Macaron hộp 6 cái": [("Hạnh nhân bột", 60), ("Đường bột", 60), ("Đường", 40), ("Trứng gà", 2),
                          ("Kem tươi (whipping cream)", 30)],
}

# tên bánh -> (trọng lượng, hạn sử dụng, bảo quản)
FACTS = {
    "Bánh kem dâu tây": ("500g", "02 ngày", "Ngăn mát tủ lạnh 2-8°C"),
    "Bánh kem socola": ("500g", "02 ngày", "Ngăn mát tủ lạnh 2-8°C"),
    "Bánh kem trà xanh": ("500g", "02 ngày", "Ngăn mát tủ lạnh 2-8°C"),
    "Bánh mì bơ sữa": ("75g", "03 ngày", "Nhiệt độ điều hoà"),
    "Bánh mì sữa tươi": ("75g", "03 ngày", "Nhiệt độ điều hoà"),
    "Cupcake vani": ("60g", "02 ngày", "Nhiệt độ điều hoà"),
    "Cupcake red velvet": ("70g", "02 ngày", "Ngăn mát tủ lạnh 2-8°C"),
    "Cookie socola chip": ("40g", "10 ngày", "Nơi khô ráo, thoáng mát"),
    "Macaron hộp 6 cái": ("90g", "05 ngày", "Ngăn mát tủ lạnh 2-8°C"),
}

# Dữ liệu MẪU - nhớ thay địa chỉ / số điện thoại bằng thông tin thật
BRANCHES = [
    ("Tài Bakery – Cầu Giấy", "25 Trần Thái Tông", "Cầu Giấy", "0901 000 001", time(7, 0), time(21, 30)),
    ("Tài Bakery – Đống Đa", "112 Tây Sơn", "Đống Đa", "0901 000 002", time(7, 0), time(21, 30)),
    ("Tài Bakery – Hai Bà Trưng", "78 Bạch Mai", "Hai Bà Trưng", "0901 000 003", time(7, 0), time(21, 30)),
    ("Tài Bakery – Hà Đông", "45 Quang Trung", "Hà Đông", "0901 000 004", time(7, 0), time(21, 0)),
]

DEMO_PASSWORD = "Taibakery@123"

# (username, họ tên, email)
USERS = [
    ("nguyenminhanh", "Nguyễn Minh Anh", "minhanh@example.com"),
    ("tranquanghuy", "Trần Quang Huy", "quanghuy@example.com"),
    ("lethuhang", "Lê Thu Hằng", "thuhang@example.com"),
    ("phamducthang", "Phạm Đức Thắng", "ducthang@example.com"),
    ("vuhoanglan", "Vũ Hoàng Lan", "hoanglan@example.com"),
    ("dothanhtung", "Đỗ Thanh Tùng", "thanhtung@example.com"),
]


class Command(BaseCommand):
    help = "Nạp thêm thành phần bánh, chi nhánh Tài Bakery và vài người dùng mẫu (chạy nhiều lần không bị trùng)"

    @transaction.atomic
    def handle(self, *args, **options):
        ing = {}
        n_ing = 0
        for name, unit, allergen, note in INGREDIENTS:
            obj, new = Ingredient.objects.get_or_create(
                name=name, defaults={"unit": unit, "is_allergen": allergen, "note": note})
            ing[name] = obj
            n_ing += new

        n_link, missing = 0, []
        for product_name, (weight, shelf, storage) in FACTS.items():
            Product.objects.filter(name=product_name, weight="", shelf_life="", storage="").update(
                weight=weight, shelf_life=shelf, storage=storage)
        for product_name, rows in RECIPES.items():
            product = Product.objects.filter(name=product_name).first()
            if not product:
                missing.append(product_name)
                continue
            for ing_name, qty in rows:
                _, new = ProductIngredient.objects.get_or_create(
                    product=product, ingredient=ing[ing_name], defaults={"quantity": Decimal(qty)})
                n_link += new

        n_br = 0
        for name, addr, district, phone, opens, closes in BRANCHES:
            _, new = Branch.objects.get_or_create(
                name=name, defaults={"address": addr, "district": district, "city": "Hà Nội",
                                     "phone": phone, "open_time": opens, "close_time": closes})
            n_br += new

        User = get_user_model()
        n_user = 0
        for username, full_name, email in USERS:
            if User.objects.filter(username=username).exists():
                continue
            User.objects.create_user(username=username, email=email, password=DEMO_PASSWORD, first_name=full_name)
            n_user += 1

        self.stdout.write(self.style.SUCCESS(
            f"Xong. Thêm {n_ing} thành phần, {n_link} dòng công thức, {n_br} chi nhánh, {n_user} người dùng."))
        if missing:
            self.stdout.write(self.style.WARNING("Không thấy sản phẩm (bỏ qua công thức): " + ", ".join(missing)))
        if n_user:
            self.stdout.write(f"Mật khẩu mẫu của người dùng mới: {DEMO_PASSWORD}")
