# Chuyển đồ án sang MySQL – Web bán bánh ngọt

## Cấu trúc CSDL (Django tự tạo bảng từ models)

| Bảng MySQL | Nội dung | Quan hệ |
|---|---|---|
| `products_category` | Danh mục bánh | 1 – N với product |
| `products_product` | Sản phẩm (tên, giá, tồn kho, ảnh…) | N – 1 category |
| `orders_order` | Đơn hàng (người nhận, SĐT, địa chỉ, trạng thái, tổng tiền) | N – 1 `auth_user` (có thể rỗng: khách vãng lai) |
| `orders_orderitem` | Chi tiết đơn (tên + giá tại lúc mua, số lượng) | N – 1 order, N – 1 product |
| `auth_user` … | Tài khoản, phân quyền (Django có sẵn) | |

## Các bước thực hiện

**1. Tạo database** – chạy `database/01_create_database.sql` bằng tài khoản root
(MySQL Workbench: mở file rồi bấm ⚡; hoặc phpMyAdmin tab SQL; hoặc `mysql -u root -p < database/01_create_database.sql`).

**2. Chép file vào project** – giải nén và chép đè vào thư mục `ĐATN` (giữ nguyên cấu trúc thư mục):
`config/settings.py`, `orders/`, `products/management/`, `database/`, `requirements.txt`.

**3. Cài thư viện** (trong venv của bạn):
```
pip install mysqlclient
```
> Nếu lỗi khi cài mysqlclient trên Windows: nâng pip (`python -m pip install -U pip`) rồi cài lại.

**4. Tạo bảng trong MySQL**
```
python manage.py makemigrations orders
python manage.py migrate
```

**5. Nạp dữ liệu**
```
python manage.py loaddata database/data_from_sqlite.json   # (tùy chọn) giữ lại tài khoản admin + dữ liệu cũ
python manage.py seed_data                                  # (tùy chọn) 9 loại bánh mẫu
python manage.py createsuperuser                            # chỉ cần nếu KHÔNG loaddata ở trên
```

**6. Chạy web**
```
python manage.py runserver
```
Vào http://127.0.0.1:8000/admin để quản lý Danh mục, Sản phẩm, Đơn hàng.

## Đổi thông tin kết nối
Mặc định trong `config/settings.py`: DB `banhngot`, user `banhngot_user`, mật khẩu `Banhngot@123`, host `127.0.0.1`, port `3306`.
Muốn dùng root/XAMPP (mật khẩu rỗng) thì đặt biến môi trường `DB_USER=root` và `DB_PASSWORD=` hoặc sửa thẳng trong settings.

## Xuất script SQL cho báo cáo
- Xem câu lệnh CREATE TABLE do Django sinh ra: `python manage.py sqlmigrate orders 0001`
- Xuất toàn bộ CSDL: `mysqldump -u root -p --databases banhngot > banhngot_backup.sql`
- Vẽ ERD: MySQL Workbench → Database → Reverse Engineer.

## Lỗi thường gặp
- `Access denied for user` → chưa chạy bước 1 hoặc sai mật khẩu trong settings.
- `Unknown database 'banhngot'` → chưa chạy bước 1.
- Báo phiên bản MySQL/MariaDB quá cũ → Django bản mới yêu cầu MySQL 8.4+ hoặc MariaDB 10.6+; hãy cập nhật hoặc cài MySQL Community 8.4.
- Chạy `migrate` lỗi 1 lần, sửa xong chạy lại là được.
