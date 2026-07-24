from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Newsletter

from .models import AcademicSession, ResultDocument, ResultPublication, SchoolClass, Student, User


@admin.register(User)
class PortalUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Portal", {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "full_name", "gender", "current_class", "active_session", "guardian_name")
    search_fields = ("student_id", "full_name", "gender", "guardian_name", "guardian_email")
    list_filter = ("current_class", "active_session")


@admin.register(ResultDocument)
class ResultDocumentAdmin(admin.ModelAdmin):
    list_display = ("student", "term", "academic_session", "school_class", "uploaded_at")
    search_fields = ("student__student_id", "student__full_name", "term")
    list_filter = ("academic_session", "school_class", "term")


admin.site.register(AcademicSession)
admin.site.register(SchoolClass)


@admin.register(ResultPublication)
class ResultPublicationAdmin(admin.ModelAdmin):
    list_display = ("academic_session", "school_class", "term", "is_published", "updated_at")
    list_filter = ("academic_session", "school_class", "is_published")
    search_fields = ("term", "academic_session__name", "school_class__name")

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "academic_session",
        "published",
        "created_at",
        "updated_at",
    )
    list_filter = ("published", "academic_session", "created_at")
    search_fields = ("title", "summary", "body", "academic_session")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("published",)
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "academic_session", "published")
        }),
        ("Content", {
            "fields": ("summary", "body", "featured_image")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
