from django.http import Http404
from django.shortcuts import render

from stores.models import Branch

from .policies import POLICIES


def about(request):
    return render(request, "core/about.html")


def contact(request):
    branches = Branch.objects.filter(is_active=True).order_by("id")
    return render(request, "core/contact.html", {"branches": branches})


def policy(request, slug):
    page = POLICIES.get(slug)
    if page is None:
        raise Http404
    links = [(k, v["title"]) for k, v in POLICIES.items()]
    return render(request, "core/policy.html", {"page": page, "slug": slug, "links": links})
