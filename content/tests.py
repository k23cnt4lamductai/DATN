from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Article, JobApplication, JobPosting
from .utils import vn_slugify


class SlugTests(TestCase):
    def test_vn_slugify_giu_chu_d(self):
        self.assertEqual(vn_slugify("Đống Đa – Hà Nội"), "dong-da-ha-noi")

    def test_slug_khong_trung(self):
        a = Article.objects.create(title="Khuyến mại tháng 12", body="x")
        b = Article.objects.create(title="Khuyến mại tháng 12", body="y")
        self.assertEqual(a.slug, "khuyen-mai-thang-12")
        self.assertEqual(b.slug, "khuyen-mai-thang-12-2")


class ArticleTests(TestCase):
    def setUp(self):
        self.news = Article.objects.create(title="Tin A", kind="news", body="a")
        self.promo = Article.objects.create(
            title="Khuyen mai B", kind="promo", body="b",
            promo_ends=timezone.localdate() + timedelta(days=5))
        self.draft = Article.objects.create(title="Nháp", body="c", is_published=False)
        self.future = Article.objects.create(
            title="Hẹn giờ", body="d", published_at=timezone.now() + timedelta(days=3))

    def test_danh_sach_chi_hien_bai_da_dang(self):
        r = self.client.get(reverse("content:news_list"))
        titles = [a.title for a in r.context["page_obj"]]
        self.assertCountEqual(titles, ["Tin A", "Khuyen mai B"])

    def test_loc_theo_loai(self):
        r = self.client.get(reverse("content:news_list"), {"kind": "promo"})
        self.assertEqual([a.title for a in r.context["page_obj"]], ["Khuyen mai B"])

    def test_loai_khong_hop_le_thi_hien_tat_ca(self):
        r = self.client.get(reverse("content:news_list"), {"kind": "hack"})
        self.assertEqual(len(r.context["page_obj"]), 2)

    def test_bai_nhap_khach_khong_xem_duoc(self):
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(self.future.get_absolute_url()).status_code, 404)

    def test_nhan_vien_xem_truoc_duoc_bai_nhap(self):
        staff = get_user_model().objects.create_user("nv", password="x", is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 200)

    def test_chi_tiet_va_trang_chu(self):
        self.assertEqual(self.client.get(self.news.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_khuyen_mai_het_han(self):
        old = Article.objects.create(
            title="Cũ", kind="promo", body="x", promo_ends=timezone.localdate() - timedelta(days=1))
        self.assertTrue(old.is_expired)
        self.assertFalse(self.promo.is_expired)
        self.assertFalse(self.news.is_expired)

    def test_trang_khong_ton_tai_va_trang_so_sai(self):
        self.assertEqual(self.client.get(reverse("content:news_detail", args=["khong-co"])).status_code, 404)
        self.assertEqual(self.client.get(reverse("content:news_list"), {"page": "abc"}).status_code, 200)


class JobTests(TestCase):
    def setUp(self):
        today = timezone.localdate()
        self.open = JobPosting.objects.create(
            title="Thợ làm bánh", description="d", deadline=today + timedelta(days=7))
        self.closed = JobPosting.objects.create(
            title="Đã hết hạn", description="d", deadline=today - timedelta(days=1))
        self.off = JobPosting.objects.create(title="Tạm dừng", description="d", is_active=False)
        self.valid = {"full_name": "Nguyễn Văn A", "phone": "0912 345 678", "email": "a@example.com", "message": "Xin chào"}

    def test_slug_tieng_viet(self):
        self.assertEqual(self.open.slug, "tho-lam-banh")

    def test_trang_danh_sach_va_chi_tiet(self):
        r = self.client.get(reverse("content:jobs"))
        self.assertEqual(r.status_code, 200)
        titles = [j.title for j in r.context["jobs"]]
        self.assertEqual(titles, ["Thợ làm bánh", "Đã hết hạn"])   # còn hạn lên trước, tin tắt không hiện
        self.assertEqual(self.client.get(self.open.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(self.off.get_absolute_url()).status_code, 404)

    def test_nop_ho_so_hop_le(self):
        r = self.client.post(self.open.get_absolute_url(), self.valid)
        self.assertRedirects(r, self.open.get_absolute_url() + "?sent=1")
        app = JobApplication.objects.get()
        self.assertEqual(app.job, self.open)
        self.assertEqual(app.phone, "0912345678")   # đã bỏ khoảng trắng

    def test_hien_loi_cam_on_sau_khi_gui(self):
        r = self.client.get(self.open.get_absolute_url(), {"sent": "1"})
        self.assertContains(r, "Đã gửi hồ sơ!")
        self.assertNotContains(r, 'name="full_name"')

    def test_so_dien_thoai_sai(self):
        r = self.client.post(self.open.get_absolute_url(), {**self.valid, "phone": "123"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(JobApplication.objects.exists())
        self.assertIn("phone", r.context["form"].errors)

    def test_o_an_chong_bot(self):
        r = self.client.post(self.open.get_absolute_url(), {**self.valid, "website": "http://spam"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(JobApplication.objects.exists())

    def test_khong_nop_duoc_khi_het_han(self):
        r = self.client.post(self.closed.get_absolute_url(), self.valid)
        self.assertRedirects(r, self.closed.get_absolute_url())
        self.assertFalse(JobApplication.objects.exists())
        self.assertFalse(self.closed.is_open)
        self.assertTrue(self.open.is_open)
