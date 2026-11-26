from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.home, name="home"),
    path("yeu-thich/", views.wishlist, name="wishlist"),
    path("yeu-thich/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
    path("san-pham/<slug:slug>/", views.detail, name="detail"),
    path("san-pham/<slug:slug>/danh-gia/", views.review_submit, name="review_submit"),
    path("san-pham/<slug:slug>/danh-gia/xoa/", views.review_delete, name="review_delete"),
]
