# Tiệm Bánh Ngọt – Web quản lý & bán bánh ngọt

Đồ án tốt nghiệp, viết bằng Django 5.2 và MySQL 8.

## Chức năng
- **Khách hàng:** xem, lọc, tìm bánh · giỏ hàng · đặt hàng · đăng ký / đăng nhập · xem lịch sử đơn · đánh giá sao và nhận xét (chỉ khách đã mua).
- **Quản trị** (`/admin/`): tổng quan, báo cáo doanh thu theo ngày, quản lý sản phẩm / đơn hàng / đánh giá, giao diện sáng – tối.

## Cài đặt
Yêu cầu: Python 3.10 trở lên (đã chạy thử với 3.13), MySQL 8.0 trở lên.

1. Chạy `database/01_create_database.sql` bằng tài khoản root của MySQL (tạo CSDL `banhngot` và tài khoản cho ứng dụng).
2. Tạo môi trường ảo và cài thư viện:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Tạo bảng và dữ liệu:
   ```
   python manage.py migrate
   python manage.py seed_data          # bánh mẫu (tùy chọn)
   python manage.py createsuperuser    # tài khoản quản trị
   ```
4. Chạy web: `python manage.py runserver` rồi mở http://127.0.0.1:8000/ (trang quản trị: `/admin/`).

## Cấu hình
- Thông tin kết nối MySQL nằm trong `config/settings.py`, hoặc đặt bằng biến môi trường `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`. Nếu đổi mật khẩu trong file SQL thì phải đổi tương ứng ở đây.
- Cho mọi tài khoản đánh giá được (không cần đã mua hàng): thêm `REVIEW_REQUIRE_PURCHASE = False` vào `config/settings.py`.

## Cấu trúc
`products` (sản phẩm, đánh giá) · `orders` (giỏ hàng, đơn hàng, báo cáo) · `accounts` (tài khoản) · `core` (giao diện dùng chung) · `config` (cài đặt) · `database` (script SQL)
