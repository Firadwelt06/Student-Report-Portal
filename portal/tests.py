from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import AcademicSession, ResultDocument, ResultPublication, SchoolClass, Student
from .views import _attach_bulk_result_pdfs


User = get_user_model()


class ResultAccessTests(TestCase):
    def setUp(self):
        self.tmpdir = TemporaryDirectory()
        self.override = override_settings(PRIVATE_MEDIA_ROOT=Path(self.tmpdir.name))
        self.override.enable()

        self.session = AcademicSession.objects.create(name="2026/2027", is_active=True)
        self.school_class = SchoolClass.objects.create(name="JSS 1A")

        self.user_one = User.objects.create_user(username="STD-001", password="StudentPass123!")
        self.user_two = User.objects.create_user(username="STD-002", password="StudentPass123!")
        self.student_one = Student.objects.create(
            user=self.user_one,
            student_id="STD-001",
            full_name="Ada Johnson",
            guardian_name="Mrs. Johnson",
            guardian_email="ada.guardian@example.com",
            current_class=self.school_class,
            active_session=self.session,
        )
        self.student_two = Student.objects.create(
            user=self.user_two,
            student_id="STD-002",
            full_name="Tunde Bello",
            guardian_name="Mr. Bello",
            guardian_email="tunde.guardian@example.com",
            current_class=self.school_class,
            active_session=self.session,
        )
        self.result = ResultDocument.objects.create(
            student=self.student_one,
            academic_session=self.session,
            school_class=self.school_class,
            term="First Term",
            pdf=SimpleUploadedFile("result.pdf", b"%PDF-1.4\nsecure result", content_type="application/pdf"),
        )

    def tearDown(self):
        self.override.disable()
        self.tmpdir.cleanup()

    def test_owner_can_view_result(self):
        ResultPublication.objects.create(
            academic_session=self.session,
            school_class=self.school_class,
            term="First Term",
            is_published=True,
        )
        self.client.login(username="STD-001", password="StudentPass123!")
        response = self.client.get(reverse("view_result", args=[self.result.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_owner_cannot_view_unpublished_result(self):
        self.client.login(username="STD-001", password="StudentPass123!")
        response = self.client.get(reverse("view_result", args=[self.result.id]))
        self.assertEqual(response.status_code, 403)

    def test_other_guardian_cannot_view_result(self):
        ResultPublication.objects.create(
            academic_session=self.session,
            school_class=self.school_class,
            term="First Term",
            is_published=True,
        )
        self.client.login(username="STD-002", password="StudentPass123!")
        response = self.client.get(reverse("view_result", args=[self.result.id]))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_is_redirected(self):
        response = self.client.get(reverse("view_result", args=[self.result.id]))
        self.assertEqual(response.status_code, 302)

    def test_bulk_result_upload_matches_pdf_by_student_full_name(self):
        admin = User.objects.create_user(username="admin", password="AdminPass123!", is_staff=True)
        attached, replaced, unmatched = _attach_bulk_result_pdfs(
            academic_session=self.session,
            school_class=self.school_class,
            term="Second Term",
            pdf_files=[
                SimpleUploadedFile("Ada Johnson.pdf", b"%PDF-1.4\nsecond term", content_type="application/pdf"),
            ],
            uploaded_by=admin,
        )

        self.assertEqual(attached, 1)
        self.assertEqual(replaced, 0)
        self.assertEqual(unmatched, [])
        self.assertTrue(
            ResultDocument.objects.filter(
                student=self.student_one,
                academic_session=self.session,
                school_class=self.school_class,
                term="Second Term",
            ).exists()
        )
