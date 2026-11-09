from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("dang-nhap/", views.CustomLoginView.as_view(), name="login"),
    path("dang-ky/", views.register, name="register"),
    path("dang-xuat/", auth_views.LogoutView.as_view(next_page="products:home"), name="logout"),
    path("don-hang-cua-toi/", views.my_orders, name="orders"),
    path("don-hang-cua-toi/<int:pk>/", views.order_detail, name="order_detail"),
]
