from django.utils.text import slugify


def vn_slugify(text):
    """slugify có xử lý chữ đ/Đ (slugify mặc định của Django làm rơi mất chữ này)."""
    return slugify(str(text).replace("đ", "d").replace("Đ", "D"))


def unique_slug(model, text, instance=None, max_length=200, fallback="bai-viet"):
    """Tạo slug chưa bị trùng trong bảng của `model` (thêm -2, -3... nếu cần)."""
    base = (vn_slugify(text) or fallback)[:max_length].strip("-") or fallback
    slug, n = base, 2
    qs = model.objects.all()
    if instance is not None and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(slug=slug).exists():
        suffix = f"-{n}"
        slug = base[: max_length - len(suffix)] + suffix
        n += 1
    return slug
