from products.models import Product

CART_SESSION_KEY = "cart"


class Cart:
    """Giỏ hàng lưu trong session: {"<id sản phẩm>": số lượng}."""

    def __init__(self, request):
        self.session = request.session
        self.data = self.session.setdefault(CART_SESSION_KEY, {})

    def _save(self):
        self.session.modified = True

    def quantity_of(self, product_id):
        return self.data.get(str(product_id), 0)

    def set_quantity(self, product_id, quantity):
        """Đặt số lượng; <= 0 thì xóa khỏi giỏ."""
        if quantity <= 0:
            self.data.pop(str(product_id), None)
        else:
            self.data[str(product_id)] = int(quantity)
        self._save()

    def remove(self, product_id):
        self.data.pop(str(product_id), None)
        self._save()

    def clear(self):
        self.session.pop(CART_SESSION_KEY, None)
        self._save()

    def __len__(self):
        """Tổng số bánh trong giỏ."""
        return sum(self.data.values())

    def __iter__(self):
        """Duyệt từng dòng: {"product", "quantity", "subtotal"} (giá lấy mới nhất từ CSDL)."""
        ids = [int(pid) for pid in self.data]
        products = {
            p.id: p
            for p in Product.objects.filter(id__in=ids, is_available=True).select_related("category")
        }
        # Bánh đã bị gỡ / ngừng bán thì tự bỏ khỏi giỏ
        missing = [pid for pid in ids if pid not in products]
        for pid in missing:
            self.data.pop(str(pid), None)
        if missing:
            self._save()

        for pid in ids:
            product = products.get(pid)
            if product is None:
                continue
            quantity = self.data[str(pid)]
            yield {
                "product": product,
                "quantity": quantity,
                "subtotal": product.price * quantity,
            }
