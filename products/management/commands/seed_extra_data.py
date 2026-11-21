from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from products.models import Ingredient, ProductIngredient, Store, StoreProduct, Product


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu nguyên liệu, 4 cửa hàng và 7 khách hàng (chạy lại không tạo trùng)"

    def handle(self, *args, **kwargs):
        ingredients = [
            ("Bột mì", "g", "Chứa gluten"), ("Trứng gà", "quả", "Chứa trứng"),
            ("Sữa tươi", "ml", "Chứa sữa"), ("Đường", "g", ""),
            ("Bơ lạt", "g", "Chứa sữa"), ("Kem tươi", "ml", "Chứa sữa"),
            ("Bột cacao", "g", ""), ("Dâu tây", "g", ""),
            ("Phô mai kem", "g", "Chứa sữa"), ("Vani", "ml", ""),
        ]
        for name, unit, note in ingredients:
            Ingredient.objects.get_or_create(name=name, defaults={"unit": unit, "allergen_note": note})

        # Bốn chi nhánh cùng thương hiệu Tài Bakery tại Hà Nội.
        # Địa chỉ chỉ mang tính minh họa, chưa phải địa chỉ kinh doanh thực tế.
        stores = [
            ("Tài Bakery – Cầu Giấy", "Cầu Giấy, Hà Nội", ""),
            ("Tài Bakery – Đống Đa", "Đống Đa, Hà Nội", ""),
            ("Tài Bakery – Hai Bà Trưng", "Hai Bà Trưng, Hà Nội", ""),
            ("Tài Bakery – Hà Đông", "Hà Đông, Hà Nội", ""),
        ]
        old_names = [
            "Sweet Cake – Hà Nội", "Bakery House – TP. Hồ Chí Minh",
            "Moon Cake – Đà Nẵng", "Happy Bakery – Hải Phòng",
        ]
        for old_name, (name, address, phone) in zip(old_names, stores):
            existing = Store.objects.filter(name=name).first()
            legacy = Store.objects.filter(name=old_name).first()
            if legacy and not existing:
                legacy.name, legacy.address, legacy.phone, legacy.is_active = name, address, phone, True
                legacy.save(update_fields=["name", "address", "phone", "is_active"])
            elif legacy and existing:
                self.stdout.write(self.style.WARNING(f"Có cả '{old_name}' và '{name}'; giữ nguyên cửa hàng cũ để tránh mất dữ liệu."))
                Store.objects.filter(pk=existing.pk).update(address=address, phone=phone, is_active=True)
            else:
                Store.objects.update_or_create(name=name, defaults={"address": address, "phone": phone, "is_active": True})

        people = [
            ("khach01", "Nguyễn Văn", "An"), ("khach02", "Trần Thị", "Bình"),
            ("khach03", "Lê Minh", "Hoàng"), ("khach04", "Phạm Thu", "Hà"),
            ("khach05", "Đỗ Quốc", "Bảo"), ("khach06", "Vũ Ngọc", "Mai"),
            ("khach07", "Hoàng Đức", "Long"),
        ]
        User = get_user_model()
        created_users = 0
        for username, first_name, last_name in people:
            user, created = User.objects.get_or_create(username=username, defaults={
                "first_name": first_name, "last_name": last_name,
                "email": f"{username}@example.com", "is_staff": False,
            })
            if created:
                user.set_unusable_password()  # Dùng lệnh đặt mật khẩu riêng nếu muốn đăng nhập
                user.save(update_fields=["password"])
                created_users += 1
        self.stdout.write(self.style.SUCCESS(f"Đã tạo {created_users} khách hàng mới, cùng nguyên liệu và cửa hàng mẫu."))
        self.stdout.write("Nguyên liệu chưa tự gán định lượng cho bánh; tồn kho cửa hàng chưa tự đồng bộ với Product.stock.")
