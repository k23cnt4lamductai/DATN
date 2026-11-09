from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.home, name="home"),
    path("san-pham/<slug:slug>/", views.detail, name="detail"),
    path("san-pham/<slug:slug>/danh-gia/", views.review_submit, name="review_submit"),
    path("san-pham/<slug:slug>/danh-gia/xoa/", views.review_delete, name="review_delete"),
]
