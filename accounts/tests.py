from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import Order

from .models import Profile

User = get_user_model()


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("an", password="Matkhau@123", first_name="An", email="an@example.com")
        self.other = User.objects.create_user("binh", password="Matkhau@123", email="binh@example.com")
        self.url = reverse("accounts:profile")
        self.data = {"full_name": "Nguyễn Văn An", "email": "an.moi@example.com",
                     "phone": "0912 345 678", "address": "12 Tây Sơn, Hà Nội", "birth_date": "1999-05-20"}

    def test_phai_dang_nhap(self):
        for name in ("accounts:profile", "accounts:password_change"):
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302)
            self.assertIn(reverse("accounts:login"), r["Location"])

    def test_xem_trang_ca_nhan(self):
        self.client.force_login(self.user)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["stats"]["total_orders"], 0)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())   # tài khoản cũ tự có hồ sơ

    def test_cap_nhat_thong_tin(self):
        self.client.force_login(self.user)
        r = self.client.post(self.url, self.data)
        self.assertRedirects(r, self.url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Nguyễn Văn An")
        self.assertEqual(self.user.email, "an.moi@example.com")
        p = self.user.profile
        self.assertEqual(p.phone, "0912345678")
        self.assertEqual(p.address, "12 Tây Sơn, Hà Nội")
        self.assertEqual(str(p.birth_date), "1999-05-20")

    def test_email_trung_nguoi_khac(self):
        self.client.force_login(self.user)
        r = self.client.post(self.url, {**self.data, "email": "BINH@example.com"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("email", r.context["form"].errors)

    def test_giu_nguyen_email_cua_minh_thi_hop_le(self):
        self.client.force_login(self.user)
        r = self.client.post(self.url, {**self.data, "email": "an@example.com"})
        self.assertRedirects(r, self.url)

    def test_du_lieu_sai(self):
        self.client.force_login(self.user)
        r = self.client.post(self.url, {**self.data, "phone": "123", "birth_date": "2999-01-01"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("phone", r.context["form"].errors)
        self.assertIn("birth_date", r.context["form"].errors)

    def test_so_dien_thoai_va_dia_chi_co_the_de_trong(self):
        self.client.force_login(self.user)
        r = self.client.post(self.url, {"full_name": "An", "email": "an@example.com"})
        self.assertRedirects(r, self.url)

    def test_thong_ke_don_hang(self):
        Order.objects.create(user=self.user, full_name="An", phone="0912345678", address="HN", total=100000, status="completed")
        Order.objects.create(user=self.user, full_name="An", phone="0912345678", address="HN", total=50000, status="pending")
        Order.objects.create(user=self.user, full_name="An", phone="0912345678", address="HN", total=70000, status="cancelled")
        Order.objects.create(user=self.other, full_name="B", phone="0912345678", address="HN", total=999999, status="completed")
        self.client.force_login(self.user)
        stats = self.client.get(self.url).context["stats"]
        self.assertEqual(stats["total_orders"], 3)
        self.assertEqual(stats["active_orders"], 1)
        self.assertEqual(stats["spent"], 150000)   # không tính đơn hủy, không tính đơn người khác

    def test_trang_don_hang_van_hoat_dong(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("accounts:orders")).status_code, 200)


class PasswordChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("an", password="Matkhau@123")
        self.client.force_login(self.user)
        self.url = reverse("accounts:password_change")

    def test_doi_mat_khau_thanh_cong_va_van_dang_nhap(self):
        r = self.client.post(self.url, {"old_password": "Matkhau@123",
                                        "new_password1": "MatKhauMoi#2026", "new_password2": "MatKhauMoi#2026"})
        self.assertRedirects(r, self.url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("MatKhauMoi#2026"))
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 200)   # chưa bị đăng xuất

    def test_sai_mat_khau_cu(self):
        r = self.client.post(self.url, {"old_password": "sai", "new_password1": "MatKhauMoi#2026", "new_password2": "MatKhauMoi#2026"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("old_password", r.context["form"].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Matkhau@123"))


class CheckoutPrefillTests(TestCase):
    def test_trang_dat_hang_dung_thong_tin_da_luu(self):
        from products.models import Category, Product
        user = User.objects.create_user("an", password="x", first_name="An", email="an@example.com")
        Profile.objects.create(user=user, phone="0912345678", address="12 Tây Sơn")
        cat = Category.objects.create(name="Bánh")
        p = Product.objects.create(category=cat, name="Bánh thử", price=10000, stock=5)
        self.client.force_login(user)
        session = self.client.session
        session["cart"] = {str(p.id): 1}
        session.save()
        r = self.client.get(reverse("orders:checkout"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["form"].initial["phone"], "0912345678")
        self.assertEqual(r.context["form"].initial["address"], "12 Tây Sơn")
