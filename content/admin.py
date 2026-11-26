from django.contrib import admin
from django.utils.html import format_html

from .models import Article, JobApplication, JobPosting, Subscriber


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "published_at", "promo_ends", "is_published", "thumb")
    list_editable = ("is_published",)
    list_filter = ("kind", "is_published")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"

    @admin.display(description="Ảnh")
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:36px;border-radius:4px;">', obj.image.url)
        return "—"


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    can_delete = False
    fields = ("full_name", "phone", "email", "created_at", "is_handled")
    readonly_fields = ("full_name", "phone", "email", "created_at")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "branch", "job_type", "headcount", "salary", "deadline", "is_active", "applicants")
    list_editable = ("is_active",)
    list_filter = ("is_active", "job_type", "branch")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [JobApplicationInline]

    @admin.display(description="Hồ sơ")
    def applicants(self, obj):
        return obj.applications.count()


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email", "job", "created_at", "is_handled")
    list_editable = ("is_handled",)
    list_filter = ("is_handled", "job")
    search_fields = ("full_name", "phone", "email")
    readonly_fields = ("job", "full_name", "phone", "email", "message", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("email",)
    date_hierarchy = "created_at"
