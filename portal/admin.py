from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AcademicSession, ResultDocument, ResultPublication, SchoolClass, Student, User


@admin.register(User)
class PortalUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Portal", {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "full_name", "current_class", "active_session", "guardian_name")
    search_fields = ("student_id", "full_name", "guardian_name", "guardian_email")
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
