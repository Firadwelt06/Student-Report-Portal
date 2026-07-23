from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .storage import private_storage


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        GUARDIAN = "GUARDIAN", "Parent or Guardian"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.GUARDIAN)

    @property
    def is_portal_admin(self):
        return self.is_staff or self.role == self.Role.ADMIN


class AcademicSession(models.Model):
    name = models.CharField(max_length=20, unique=True, help_text="Example: 2026/2027")
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class SchoolClass(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Example: JSS 1A")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=150)
    guardian_name = models.CharField(max_length=150)
    guardian_email = models.EmailField(blank=True)
    current_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="students")
    active_session = models.ForeignKey(AcademicSession, on_delete=models.PROTECT, related_name="students")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"


def result_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"results/{instance.student.student_id}/{uuid4().hex}{extension}"


def validate_pdf(file):
    if not file.name.lower().endswith(".pdf"):
        raise ValidationError("Only PDF files are allowed.")
    header = file.read(4)
    file.seek(0)
    if header != b"%PDF":
        raise ValidationError("The uploaded file does not appear to be a valid PDF.")


class ResultDocument(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.PROTECT, related_name="results")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="results")
    term = models.CharField(max_length=30, help_text="Example: First Term")
    pdf = models.FileField(upload_to=result_upload_path, storage=private_storage, validators=[validate_pdf])
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "academic_session", "school_class", "term"],
                name="unique_result_per_student_session_class_term",
            )
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.term} - {self.academic_session}"


class ResultPublication(models.Model):
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="result_publications")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="result_publications")
    term = models.CharField(max_length=30, help_text="Example: First Term")
    is_published = models.BooleanField(default=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-academic_session__name", "school_class__name", "term"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_session", "school_class", "term"],
                name="unique_publication_per_session_class_term",
            )
        ]

    def __str__(self):
        status = "Published" if self.is_published else "Unpublished"
        return f"{self.academic_session} - {self.school_class} - {self.term} ({status})"
