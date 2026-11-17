from decimal import ROUND_HALF_UP, Decimal


def calc_new_price(price, percent, direction, round_to="0"):
    """Giá mới sau khi giảm / tăng `percent`%.
    direction: "down" (giảm) hoặc "up" (tăng); round_to: "0", "500" hoặc "1000" (làm tròn đến bội số)."""
    percent = Decimal(percent)
    factor = (Decimal(100) - percent if direction == "down" else Decimal(100) + percent) / Decimal(100)
    value = Decimal(price) * factor
    step = Decimal(round_to or 0)
    if step > 0:
        value = (value / step).quantize(Decimal(1), rounding=ROUND_HALF_UP) * step
    else:
        value = value.quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return max(value, Decimal(0))
