from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from content.models import Article, JobPosting
from stores.models import Branch

K = Article.Kind
T = JobPosting.JobType

# Nội dung MẪU để xem giao diện - bạn sửa / xóa / viết bài thật trong trang quản trị.
# (tiêu đề, loại, mô tả ngắn, nội dung, số ngày kể từ hôm nay đến khi hết khuyến mại (None = không giới hạn), đăng cách đây bao nhiêu ngày)
ARTICLES = [
    ("Tài Bakery khai trương chi nhánh Hai Bà Trưng", K.NEWS,
     "Thêm một địa chỉ mới để bạn dễ dàng ghé thưởng thức bánh tươi mỗi ngày.",
     "Sau thời gian được khách hàng yêu mến, Tài Bakery vui mừng mở thêm chi nhánh tại quận Hai Bà Trưng.\n\n"
     "Tại đây, bạn có thể chọn bánh ngay tại quầy, đặt bánh sinh nhật theo yêu cầu hoặc nhờ nhân viên tư vấn loại bánh phù hợp với buổi tiệc của mình.\n\n"
     "Chúng tôi mong được đón bạn trong những ngày khai trương.", None, 3),
    ("Bí quyết chọn bánh sinh nhật cho từng độ tuổi", K.NEWS,
     "Gợi ý nhanh giúp bạn chọn đúng chiếc bánh cho người thân, bạn bè và đồng nghiệp.",
     "Với trẻ nhỏ, bạn nên chọn bánh ít ngọt, trang trí màu sắc vui mắt. Với người lớn tuổi, bánh kem trà xanh hoặc bánh mì ngọt nhẹ thường được yêu thích hơn.\n\n"
     "Nếu cần bánh cho đông người, hãy đặt trước ít nhất một ngày để tiệm chuẩn bị chu đáo.\n\n"
     "Bạn có thể ghi chú chữ trên bánh và giờ nhận ngay ở bước đặt hàng.", None, 10),
    ("Vì sao bánh tươi nên dùng trong ngày?", K.NEWS,
     "Bánh làm từ bơ, sữa và kem tươi ngon nhất khi dùng sớm sau khi ra lò.",
     "Bánh của Tài Bakery không dùng chất bảo quản, vì vậy hương vị và độ mềm ngon nhất trong ngày đầu tiên.\n\n"
     "Bạn nên bảo quản bánh kem trong ngăn mát tủ lạnh và dùng trong vòng hai ngày. Các loại bánh mì ngọt có thể để ở nhiệt độ phòng nơi khô ráo.", None, 20),
    ("Giảm 15% bánh kem trong tháng 12", K.PROMO,
     "Ưu đãi dành cho tất cả các loại bánh kem khi đặt hàng trên website.",
     "Trong suốt tháng 12, Tài Bakery giảm 15% cho các loại bánh kem khi đặt hàng trực tuyến.\n\n"
     "Ưu đãi áp dụng cho mọi chi nhánh và không áp dụng đồng thời với chương trình khác.\n\n"
     "Đặt bánh ngay để nhận ưu đãi.", 38, 1),
    ("Mua 2 tặng 1 cookie socola chip cuối tuần", K.PROMO,
     "Cuối tuần ngọt ngào hơn với ưu đãi mua 2 tặng 1 dành cho cookie.",
     "Vào thứ Bảy và Chủ nhật hằng tuần, mua 2 hộp cookie socola chip bạn sẽ được tặng thêm 1 hộp.\n\n"
     "Số lượng ưu đãi có hạn mỗi ngày, vì vậy bạn nên đặt sớm.", 20, 2),
    ("Miễn phí giao hàng cho đơn từ 200.000đ", K.PROMO,
     "Giao bánh tận nơi, tươi ngon, không tính phí vận chuyển cho đơn từ 200.000đ.",
     "Tài Bakery miễn phí giao hàng nội thành cho các đơn từ 200.000đ.\n\n"
     "Bạn chọn ngày nhận bánh ở bước đặt hàng, nhân viên sẽ gọi xác nhận trước khi giao.", None, 5),
    ("Ưu đãi Halloween – Bánh bí ngô", K.PROMO,
     "Chương trình đã kết thúc, cảm ơn bạn đã ủng hộ.",
     "Chương trình Halloween đã kết thúc. Hẹn gặp bạn ở những ưu đãi tiếp theo của Tài Bakery.", -23, 40),
]

JOBS = [
    ("Nhân viên bán hàng", "Cầu Giấy", T.FULL, 2, "7 – 9 triệu đồng/tháng",
     "Tư vấn và bán bánh tại quầy, giữ gìn quầy bánh gọn gàng, thu ngân và chăm sóc khách hàng.",
     "Giao tiếp tốt, thân thiện, nhanh nhẹn\nƯu tiên có kinh nghiệm bán hàng ngành thực phẩm\nLàm việc theo ca, có thể đứng quầy lâu",
     "Lương cứng cộng thưởng doanh số\nĐược đào tạo kiến thức về sản phẩm\nĂn ca và bánh tặng cuối ngày", 30),
    ("Thợ làm bánh", None, T.FULL, 3, "10 – 15 triệu đồng/tháng",
     "Chuẩn bị nguyên liệu, nướng bánh và trang trí bánh theo công thức của tiệm, giữ vệ sinh khu bếp.",
     "Có kinh nghiệm làm bánh hoặc đã học nghề làm bánh\nTỉ mỉ, đúng giờ, chịu khó\nSẵn sàng làm ca sáng sớm",
     "Thu nhập theo tay nghề\nĐược học thêm công thức mới\nBảo hiểm theo quy định", 45),
    ("Nhân viên giao hàng", "Hà Đông", T.PART, 2, "25.000đ/giờ + thưởng chuyến",
     "Nhận bánh đã đóng gói và giao tận nơi cho khách đúng giờ, giữ bánh nguyên vẹn.",
     "Có xe máy và bằng lái hợp lệ\nRành đường khu vực nội thành\nTrung thực, đúng hẹn",
     "Giờ làm linh hoạt\nHỗ trợ xăng xe\nThưởng theo số chuyến giao", 20),
    ("Thực tập sinh Marketing", None, T.INTERN, 1, "Thỏa thuận",
     "Hỗ trợ chụp ảnh sản phẩm, viết nội dung bài đăng và cập nhật tin tức, khuyến mại cho website và mạng xã hội.",
     "Sinh viên năm 3 – 4 ngành Marketing, Truyền thông hoặc liên quan\nBiết chụp và chỉnh ảnh cơ bản\nViết lách tốt",
     "Được hướng dẫn trực tiếp\nCó giấy xác nhận thực tập\nƯu tiên nhận chính thức sau thực tập", 25),
]


class Command(BaseCommand):
    help = "Nạp bài tin tức, khuyến mại và tin tuyển dụng MẪU (chạy nhiều lần không bị trùng)"

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()
        today = timezone.localdate()

        n_art = 0
        for title, kind, summary, body, promo_days, posted_days_ago in ARTICLES:
            _, new = Article.objects.get_or_create(
                title=title,
                defaults={
                    "kind": kind, "summary": summary, "body": body,
                    "published_at": now - timedelta(days=posted_days_ago),
                    "promo_ends": today + timedelta(days=promo_days) if promo_days is not None else None,
                },
            )
            n_art += new

        branches = {b.district: b for b in Branch.objects.all()}
        n_job = 0
        for title, district, job_type, headcount, salary, desc, req, ben, days in JOBS:
            _, new = JobPosting.objects.get_or_create(
                title=title,
                defaults={
                    "branch": branches.get(district) if district else None,
                    "job_type": job_type, "headcount": headcount, "salary": salary,
                    "description": desc, "requirements": req, "benefits": ben,
                    "deadline": today + timedelta(days=days),
                },
            )
            n_job += new

        self.stdout.write(self.style.SUCCESS(f"Xong. Thêm {n_art} bài viết, {n_job} tin tuyển dụng."))
