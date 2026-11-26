"""Thông tin cửa hàng.
Sửa ở đây là cập nhật toàn bộ website: đầu trang, chân trang, trang chủ, trang Giới thiệu và Liên hệ.
Các giá trị bên dưới chỉ là VÍ DỤ - hãy thay bằng thông tin thật của cửa hàng.
"""

SHOP_INFO = {
    # ---------- Thương hiệu ----------
    "name": "Tài Bakery",
    "tagline": "Bánh ngọt tươi mỗi ngày",
    "slogan": "Làm thủ công từ nguyên liệu chọn lọc – ngọt vừa, thơm lâu.",

    # Dòng thông báo / khuyến mãi chạy trên cùng mọi trang. Để "" để tắt.
    "announcement": "TÀI BAKERY – HOTLINE: 0901 000 001",

    # Ảnh bìa trang chủ (tùy chọn). Ví dụ: "/media/banner.jpg" (để file trong thư mục media/).
    # Để "" thì dùng nền màu mặc định.
    "hero_image": "",

    # Dòng "Giao hàng" trong khung Thông tin sản phẩm. Để "" để ẩn.
    "delivery_note": "Giao hàng tận nơi chỉ áp dụng cho đơn từ 200.000đ",

    # ---------- Liên hệ (VÍ DỤ - sửa thành thông tin thật) ----------
    "address": "25 Trần Thái Tông, Cầu Giấy, Hà Nội",
    "phone": "0901 000 001",
    "email": "lienhe@taibakery.example",
    "map_query": "",            # từ khóa tìm trên Google Maps; để "" thì dùng địa chỉ ở trên
    "facebook": "",             # dán link đầy đủ (https://...), để "" nếu không có
    "zalo": "",
    "instagram": "",
    "hours": [                  # (ngày, giờ)
        ("Thứ 2 – Thứ 6", "7:00 – 21:00"),
        ("Thứ 7 – Chủ nhật", "7:00 – 22:00"),
    ],

    # ---------- Trang Giới thiệu (mỗi dòng là một đoạn văn) ----------
    "about": [
        "Tài Bakery bắt đầu từ niềm yêu thích làm bánh thủ công. Mỗi chiếc bánh được làm mới trong ngày, "
        "từ những nguyên liệu chọn lọc, với vị ngọt vừa phải để ai cũng có thể thưởng thức.",
        "Chúng tôi nhận làm bánh sinh nhật, bánh tặng và bánh theo yêu cầu. Bạn chỉ cần ghi chú ở bước đặt hàng "
        "(chữ viết trên bánh, giờ muốn nhận...), chúng tôi sẽ liên hệ xác nhận với bạn.",
    ],

    # ---------- Điểm nổi bật dưới banner trang chủ ----------
    # Tài khoản nhận chuyển khoản (DỮ LIỆU MẪU - thay bằng tài khoản thật).
    # bank_id là mã ngân hàng theo VietQR: VCB, TCB, MB, ACB, BIDV, ICB (VietinBank), VPB, TPB...
    "bank": {
        "bank_id": "VCB",
        "bank_name": "Vietcombank",
        "account_no": "0123456789",
        "account_name": "TAI BAKERY",
    },
    "promos": [
        {"icon": "🎂", "title": "Bánh làm mới mỗi ngày", "text": "Làm thủ công, không để bánh tồn lâu.", "link": "/#san-pham"},
        {"icon": "🚚", "title": "Giao hàng tận nơi", "text": "Chọn ngày muốn nhận ngay khi đặt hàng.", "link": "/chinh-sach/giao-hang/"},
        {"icon": "💝", "title": "Nhận làm theo yêu cầu", "text": "Ghi chú chữ trên bánh, giờ nhận... ở bước đặt hàng.", "link": "/lien-he/#dat-banh"},
        {"icon": "🔄", "title": "Đổi trả nếu bánh lỗi", "text": "Hỗ trợ đổi hoặc hoàn tiền khi bánh sai, hỏng.", "link": "/chinh-sach/doi-tra/"},
    ],
}
