-- =====================================================
--  Tạo CSDL MySQL cho đồ án: Web quản lý & bán bánh ngọt
--  Chạy 1 lần bằng tài khoản root (MySQL Workbench / phpMyAdmin / CMD)
--    mysql -u root -p < 01_create_database.sql
-- =====================================================

CREATE DATABASE IF NOT EXISTS banhngot
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Tài khoản riêng cho ứng dụng (đổi mật khẩu nếu muốn,
-- nhớ sửa lại tương ứng trong config/settings.py)
CREATE USER IF NOT EXISTS 'banhngot_user'@'localhost' IDENTIFIED BY 'Banhngot@123';
GRANT ALL PRIVILEGES ON banhngot.* TO 'banhngot_user'@'localhost';

-- Django cần quyền tạo DB "test_banhngot" khi chạy `manage.py test`
GRANT ALL PRIVILEGES ON `test\_banhngot`.* TO 'banhngot_user'@'localhost';

FLUSH PRIVILEGES;
