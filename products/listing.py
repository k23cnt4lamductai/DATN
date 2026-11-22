"""Hàm hỗ trợ cho trang danh sách bánh: đọc bộ lọc, tạo liên kết, tính dãy số trang.
(Thuần Python, không dùng cơ sở dữ liệu nên dễ kiểm thử.)"""
from urllib.parse import urlencode

SORTS = [
    ("new", "Mới nhất"),
    ("popular", "Bán chạy nhất"),
    ("rating", "Đánh giá cao"),
    ("price_asc", "Giá thấp → cao"),
    ("price_desc", "Giá cao → thấp"),
]
DEFAULT_SORT = "new"
PAGE_SIZE = 12


def clean_int(value):
    """Số nguyên không âm, hoặc None nếu bỏ trống / sai định dạng."""
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def parse_filters(get):
    """Đọc các tham số trên đường dẫn (category, q, sort, min_price, max_price)."""
    sort = get.get("sort")
    if sort not in dict(SORTS):
        sort = DEFAULT_SORT
    low, high = clean_int(get.get("min_price")), clean_int(get.get("max_price"))
    if low is not None and high is not None and low > high:
        low, high = high, low                      # khách nhập ngược thì tự đổi chỗ
    return {
        "category": (get.get("category") or "").strip(),
        "q": (get.get("q") or "").strip(),
        "sort": sort,
        "min_price": low,
        "max_price": high,
    }


def make_url(base, items, **updates):
    """Tạo đường dẫn từ các tham số hiện có (items = các cặp khóa-giá trị) rồi áp dụng thay đổi.
    updates: khóa=None (hoặc "") thì bỏ, khóa=giá trị thì đặt lại. Luôn bỏ tham số `page` cũ."""
    pairs = [(k, v) for k, v in items if k not in updates and k != "page"]
    for key, value in updates.items():
        if value is not None and value != "":
            pairs.append((key, str(value)))
    query = urlencode(pairs)
    return base + ("?" + query if query else "")


def page_items(current, total, on_each_side=2, on_ends=1):
    """Dãy số trang rút gọn, None là dấu '…'. Ví dụ: [1, None, 4, 5, 6, 7, 8, None, 20]."""
    if total < 1:
        return []
    keep = set(range(1, min(on_ends, total) + 1))
    keep |= set(range(max(total - on_ends + 1, 1), total + 1))
    keep |= set(range(max(current - on_each_side, 1), min(current + on_each_side, total) + 1))
    items, previous = [], 0
    for number in sorted(keep):
        if previous and number - previous > 1:
            items.append(previous + 1 if number - previous == 2 else None)   # khoảng trống 1 trang thì hiện luôn số
        items.append(number)
        previous = number
    return items
