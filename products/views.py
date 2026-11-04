from django.shortcuts import render
from .models import Category, Product


def home(request):
    products = Product.objects.filter(is_available=True).select_related("category")
    categories = Category.objects.all()

    category_slug = request.GET.get("category")
    keyword = request.GET.get("q")

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if keyword:
        products = products.filter(name__icontains=keyword)

    return render(request, "products/home.html", {
        "products": products,
        "categories": categories,
        "current_category": category_slug,
        "keyword": keyword or "",
    })