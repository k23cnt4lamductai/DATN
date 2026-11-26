"""Nạp thêm bánh để mỗi danh mục có khoảng 6 sản phẩm (kèm thành phần, hạn dùng, bảo quản).

Chạy:  python manage.py seed_more
Chạy lại nhiều lần không bị trùng. Ảnh sản phẩm thêm sau qua trang quản trị.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Category, Ingredient, Product, ProductIngredient

U = Ingredient.Unit

# (tên, đơn vị, có thể gây dị ứng, ghi chú) - đã có thì giữ nguyên, chưa có thì tạo
INGREDIENTS = [
    ("Bột mì", U.GRAM, True, "Chứa gluten"),
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
    ("Cà phê", U.GRAM, False, ""),
    ("Xoài", U.GRAM, False, ""),
    ("Chanh dây", U.GRAM, False, ""),
    ("Nho khô", U.GRAM, False, ""),
    ("Yến mạch", U.GRAM, False, ""),
]

KEM = ("Ngăn mát tủ lạnh 2-8°C", "02 ngày")
ROOM = ("Nhiệt độ điều hoà", "03 ngày")

# Danh mục -> [(tên, mô tả, giá, tồn, trọng lượng, hạn dùng, bảo quản, [(thành phần, định lượng)])]
DATA = {
    "Bánh kem": [
        ("Bánh kem tiramisu", "Cốt bánh thấm cà phê, kem phô mai mềm mịn, rắc cacao.", 390000, 6, "500g", "02 ngày", "Ngăn mát tủ lạnh 2-8°C",
         [("Bột mì", 100), ("Trứng gà", 4), ("Đường", 100), ("Phô mai kem (cream cheese)", 250),
          ("Kem tươi (whipping cream)", 200), ("Cà phê", 15), ("Bột cacao", 15)]),
        ("Bánh kem xoài", "Kem tươi nhẹ béo cùng xoài chín ngọt thơm.", 370000, 6, "500g", "02 ngày", "Ngăn mát tủ lạnh 2-8°C",
         [("Bột mì", 120), ("Trứng gà", 4), ("Đường", 100), ("Kem tươi (whipping cream)", 300), ("Xoài", 250), ("Vani", 1)]),
        ("Bánh kem phô mai chanh dây", "Vị phô mai béo cân bằng với chanh dây chua nhẹ.", 395000, 5, "500g", "02 ngày", "Ngăn mát tủ lạnh 2-8°C",
         [("Phô mai kem (cream cheese)", 300), ("Kem tươi (whipping cream)", 200), ("Trứng gà", 3),
          ("Đường", 90), ("Chanh dây", 80), ("Bột mì", 60)]),
    ],
    "Bánh mì ngọt": [
        ("Bánh mì socola", "Ruột mềm, nhân socola chảy ngọt dịu.", 30000, 35, "80g", "03 ngày", "Nhiệt độ điều hoà",
         [("Bột mì", 60), ("Socola đen", 20), ("Sữa tươi", 25), ("Đường", 7), ("Men nở", 1), ("Bơ lạt", 8)]),
        ("Bánh mì phô mai", "Phô mai béo mặn nhẹ trên nền bánh mì bơ sữa.", 32000, 30, "85g", "03 ngày", "Nhiệt độ điều hoà",
         [("Bột mì", 60), ("Phô mai kem (cream cheese)", 25), ("Sữa tươi", 25), ("Bơ lạt", 8), ("Men nở", 1), ("Muối", 1)]),
        ("Bánh mì nho khô", "Bánh mì mềm xen nho khô thơm ngọt tự nhiên.", 28000, 35, "80g", "03 ngày", "Nhiệt độ điều hoà",
         [("Bột mì", 60), ("Nho khô", 20), ("Sữa tươi", 25), ("Đường", 8), ("Men nở", 1), ("Trứng gà", 1)]),
        ("Bánh mì kem trứng", "Nhân kem trứng sữa béo mịn, vỏ bánh vàng bóng.", 26000, 35, "80g", "03 ngày", "Nhiệt độ điều hoà",
         [("Bột mì", 55), ("Trứng gà", 2), ("Sữa tươi", 35), ("Kem tươi (whipping cream)", 15), ("Đường", 8), ("Men nở", 1)]),
    ],
    "Bánh cupcake": [
        ("Cupcake socola", "Cốt cacao đậm vị phủ kem socola.", 32000, 30, "70g", "02 ngày", "Nhiệt độ điều hoà",
         [("Bột mì", 35), ("Bột cacao", 8), ("Bơ lạt", 25), ("Đường", 30), ("Trứng gà", 1), ("Socola đen", 15)]),
        ("Cupcake dâu tây", "Cốt vani mềm, kem bơ dâu tây tươi mát.", 35000, 28, "65g", "02 ngày", "Nhiệt độ điều hoà",
         [("Bột mì", 35), ("Bơ lạt", 25), ("Đường", 30), ("Trứng gà", 1), ("Dâu tây", 25), ("Vani", 1)]),
        ("Cupcake trà xanh", "Hương matcha thanh nhẹ, ít ngọt.", 34000, 28, "65g", "02 ngày", "Nhiệt độ điều hoà",
         [("Bột mì", 35), ("Bột trà xanh matcha", 4), ("Bơ lạt", 25), ("Đường", 28), ("Trứng gà", 1), ("Sữa tươi", 20)]),
        ("Cupcake cà phê", "Cốt bánh thơm cà phê, kem bơ vani béo nhẹ.", 36000, 25, "70g", "02 ngày", "Nhiệt độ điều hoà",
         [("Bột mì", 35), ("Cà phê", 4), ("Bơ lạt", 25), ("Đường", 30), ("Trứng gà", 1), ("Vani", 1)]),
    ],
    "Bánh quy": [
        ("Cookie yến mạch nho khô", "Giòn dai, nhiều yến mạch và nho khô.", 18000, 50, "45g", "10 ngày", "Nơi khô ráo, thoáng mát",
         [("Yến mạch", 20), ("Bột mì", 20), ("Bơ lạt", 20), ("Đường", 15), ("Nho khô", 10), ("Trứng gà", 1)]),
        ("Cookie bơ", "Cookie bơ thơm, tan trong miệng.", 12000, 60, "35g", "10 ngày", "Nơi khô ráo, thoáng mát",
         [("Bột mì", 30), ("Bơ lạt", 25), ("Đường bột", 12), ("Trứng gà", 1), ("Vani", 1)]),
        ("Cookie trà xanh", "Cookie matcha giòn nhẹ, vị trà thanh.", 16000, 50, "40g", "10 ngày", "Nơi khô ráo, thoáng mát",
         [("Bột mì", 28), ("Bột trà xanh matcha", 3), ("Bơ lạt", 22), ("Đường", 14), ("Trứng gà", 1)]),
        ("Macaron hộp 12 cái", "Hộp 12 macaron nhiều vị, hợp làm quà tặng.", 230000, 12, "180g", "05 ngày", "Ngăn mát tủ lạnh 2-8°C",
         [("Hạnh nhân bột", 120), ("Đường bột", 120), ("Đường", 80), ("Trứng gà", 4), ("Kem tươi (whipping cream)", 60)]),
    ],
}


class Command(BaseCommand):
    help = "Thêm khoảng 6 sản phẩm cho mỗi danh mục (chạy nhiều lần không bị trùng)"

    @transaction.atomic
    def handle(self, *args, **options):
        ing = {}
        for name, unit, allergen, note in INGREDIENTS:
            ing[name], _ = Ingredient.objects.get_or_create(
                name=name, defaults={"unit": unit, "is_allergen": allergen, "note": note})

        n_new = 0
        for cat_name, items in DATA.items():
            category, _ = Category.objects.get_or_create(name=cat_name)
            for name, desc, price, stock, weight, shelf, storage, recipe in items:
                product, is_new = Product.objects.get_or_create(
                    name=name,
                    defaults={"category": category, "description": desc, "price": price, "stock": stock,
                              "weight": weight, "shelf_life": shelf, "storage": storage},
                )
                n_new += is_new
                for ing_name, qty in recipe:
                    ProductIngredient.objects.get_or_create(
                        product=product, ingredient=ing[ing_name], defaults={"quantity": Decimal(qty)})

        self.stdout.write(self.style.SUCCESS(f"Xong. Đã thêm {n_new} sản phẩm mới."))
        for cat in Category.objects.all():
            self.stdout.write(f"  {cat.name}: {cat.products.count()} sản phẩm")
        self.stdout.write("Nhớ thêm ảnh cho sản phẩm mới trong trang quản trị (mục Sản phẩm).")
