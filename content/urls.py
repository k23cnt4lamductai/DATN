from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("tin-tuc/", views.news_list, name="news_list"),
    path("tin-tuc/<slug:slug>/", views.news_detail, name="news_detail"),
    path("tuyen-dung/", views.jobs_list, name="jobs"),
    path("tuyen-dung/<slug:slug>/", views.job_detail, name="job_detail"),
]
