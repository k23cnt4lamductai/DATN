from django.shortcuts import render

from stores.models import Branch


def about(request):
    return render(request, "core/about.html")


def contact(request):
    branches = Branch.objects.filter(is_active=True).order_by("id")
    return render(request, "core/contact.html", {"branches": branches})
