from pathlib import Path
import csv
import io
import re

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import ProtectedError
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .decorators import admin_required
from .forms import (
    AcademicSessionForm,
    AdminPasswordResetForm,
    BulkResultUploadForm,
    PortalLoginForm,
    ResultDocumentForm,
    ResultPublicationForm,
    SchoolClassForm,
    StudentCSVImportForm,
    StudentForm,
)
from .models import AcademicSession, ResultDocument, ResultPublication, SchoolClass, Student, User


def home(request):
    return render(request, "portal/home.html")


class PortalLoginView(LoginView):
    template_name = "portal/login.html"
    authentication_form = PortalLoginForm

    def get_success_url(self):
        if self.request.user.is_portal_admin:
            return reverse_lazy("admin_dashboard")
        return reverse_lazy("dashboard")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def dashboard(request):
    if request.user.is_portal_admin:
        return redirect("admin_dashboard")
    student = get_object_or_404(Student, user=request.user)
    published_terms = ResultPublication.objects.filter(
        is_published=True,
        academic_session=student.active_session,
        school_class=student.current_class,
    ).values_list("term", flat=True)
    results = student.results.select_related("academic_session", "school_class").filter(
        academic_session=student.active_session,
        school_class=student.current_class,
        term__in=published_terms,
    )
    return render(request, "portal/dashboard.html", {"student": student, "results": results})


def _authorize_result_access(request, result_id):
    result = get_object_or_404(ResultDocument.objects.select_related("student", "academic_session", "school_class"), pk=result_id)
    if request.user.is_portal_admin:
        return result
    if not hasattr(request.user, "student_profile") or result.student.user_id != request.user.id:
        raise PermissionDenied("You do not have access to this result.")
    is_published = ResultPublication.objects.filter(
        academic_session=result.academic_session,
        school_class=result.school_class,
        term=result.term,
        is_published=True,
    ).exists()
    if not is_published:
        raise PermissionDenied("This result has not been published yet.")
    return result


@login_required
@xframe_options_sameorigin
def view_result(request, result_id):
    result = _authorize_result_access(request, result_id)
    if not result.pdf:
        raise Http404("Result file not found.")
    response = FileResponse(result.pdf.open("rb"), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{Path(result.pdf.name).name}"'
    response["Cache-Control"] = "private, no-store"
    return response


@login_required
def download_result(request, result_id):
    result = _authorize_result_access(request, result_id)
    if not result.pdf:
        raise Http404("Result file not found.")
    response = FileResponse(result.pdf.open("rb"), content_type="application/pdf", as_attachment=True, filename=Path(result.pdf.name).name)
    response["Cache-Control"] = "private, no-store"
    return response

@login_required
def submit_feedback(request):
    if request.method == "POST":
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        contact = request.POST.get("contact", "not provided")
        student_id = request.POST.get("student_id")

        send_mail(
            subject=f"[Portal Feedback] {subject}",
            message=f"Student ID: {student_id}\nContact: {contact}\n\n{message}",
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=["adeleyebukola587@gmail.com"],
        )
        messages.success(request, "Thanks — your feedback has been sent to the school office.")
    return redirect("dashboard")
    
@admin_required
def admin_dashboard(request):
    query = request.GET.get("q", "").strip()
    students = Student.objects.select_related("current_class", "active_session")
    if query:
        students = students.filter(
            Q(student_id__icontains=query)
            | Q(full_name__icontains=query)
            | Q(guardian_name__icontains=query)
            | Q(guardian_email__icontains=query)
        )
    context = {
        "query": query,
        "students": students[:50],
        "student_count": Student.objects.count(),
        "result_count": ResultDocument.objects.count(),
        "class_count": SchoolClass.objects.count(),
        "session_count": AcademicSession.objects.count(),
        "published_term_count": ResultPublication.objects.filter(is_published=True).count(),
    }
    return render(request, "portal/admin_dashboard.html", context)


@admin_required
def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student created successfully.")
        return redirect("admin_dashboard")
    return render(request, "portal/form.html", {"form": form, "title": "Add Student"})


@admin_required
def student_edit(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student updated successfully.")
        return redirect("admin_dashboard")
    return render(request, "portal/form.html", {"form": form, "title": "Edit Student"})


@admin_required
def student_delete(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == "POST":
        student.user.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect("admin_dashboard")
    return render(request, "portal/confirm_delete.html", {"object": student, "title": "Delete Student"})


@admin_required
def reset_student_password(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    form = AdminPasswordResetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        student.user.set_password(form.cleaned_data["new_password"])
        student.user.save()
        messages.success(request, "Password reset successfully.")
        return redirect("admin_dashboard")
    return render(request, "portal/form.html", {"form": form, "title": f"Reset Password: {student.full_name}"})


@admin_required
def result_upload(request):
    form = ResultDocumentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        result = form.save(commit=False)
        result.uploaded_by = request.user
        result.save()
        messages.success(request, "Result PDF uploaded successfully.")
        return redirect("admin_dashboard")
    return render(request, "portal/form.html", {"form": form, "title": "Upload Result PDF"})


@admin_required
def bulk_result_upload(request):
    form = BulkResultUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            attached, replaced, unmatched = _attach_bulk_result_pdfs(
                academic_session=form.cleaned_data["academic_session"],
                school_class=form.cleaned_data["school_class"],
                term=form.cleaned_data["term"],
                pdf_files=form.cleaned_data["pdf_files"],
                uploaded_by=request.user,
            )
        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)
        else:
            messages.success(request, f"Bulk result upload complete. Attached {attached}, replaced {replaced}.")
            for filename in unmatched:
                messages.warning(request, f"No matching learner found for {filename}.")
            return redirect("admin_dashboard")
    return render(request, "portal/bulk_result_upload.html", {"form": form, "title": "Bulk Result PDF Upload"})


def _normalize_match_name(value):
    stem = Path(value).stem
    return re.sub(r"[^a-z0-9]+", " ", stem.lower()).strip()


def _attach_bulk_result_pdfs(academic_session, school_class, term, pdf_files, uploaded_by):
    students = Student.objects.filter(active_session=academic_session, current_class=school_class)
    student_map = {}
    duplicate_names = set()

    for student in students:
        key = _normalize_match_name(student.full_name)
        if key in student_map:
            duplicate_names.add(student.full_name)
        student_map[key] = student

    if duplicate_names:
        raise ValidationError(
            "Duplicate learner full name(s) in this class/session: "
            + ", ".join(sorted(duplicate_names))
            + ". Use unique names or Student ID based filenames before importing."
        )

    attached = 0
    replaced = 0
    unmatched = []

    with transaction.atomic():
        for pdf_file in pdf_files:
            student = student_map.get(_normalize_match_name(pdf_file.name))
            if not student:
                unmatched.append(pdf_file.name)
                continue

            _, created = ResultDocument.objects.update_or_create(
                student=student,
                academic_session=academic_session,
                school_class=school_class,
                term=term,
                defaults={"pdf": pdf_file, "uploaded_by": uploaded_by},
            )
            if created:
                attached += 1
            else:
                replaced += 1

    return attached, replaced, unmatched


@admin_required
def student_csv_import(request):
    form = StudentCSVImportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            imported, updated = _import_students_from_csv(form.cleaned_data["csv_file"])
        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)
        else:
            messages.success(request, f"Student import complete. Created {imported}, updated {updated}.")
            return redirect("admin_dashboard")
    return render(
        request,
        "portal/csv_import.html",
        {
            "form": form,
            "title": "Bulk Student CSV Import",
            "required_headings": REQUIRED_STUDENT_CSV_HEADINGS,
        },
    )


REQUIRED_STUDENT_CSV_HEADINGS = [
    "student_id",
    "student_name",
    "gender",
    "class_name",
    "academic_session",
    "temporary_password",
]


def _import_students_from_csv(csv_file):
    decoded = csv_file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    headings = set(reader.fieldnames or [])
    missing = [heading for heading in REQUIRED_STUDENT_CSV_HEADINGS if heading not in headings]
    if missing:
        raise ValidationError(f"Missing CSV heading(s): {', '.join(missing)}")

    rows = list(reader)
    if not rows:
        raise ValidationError("The CSV file has no student rows.")

    created = 0
    updated = 0
    row_errors = []

    with transaction.atomic():
        for index, row in enumerate(rows, start=2):
            cleaned = {key: (row.get(key) or "").strip() for key in REQUIRED_STUDENT_CSV_HEADINGS}
            student = Student.objects.filter(student_id=cleaned["student_id"]).select_related("user").first()
            required_missing = [
                key
                for key, value in cleaned.items()
                if key not in ["temporary_password"] and not value
            ]
            if not student and not cleaned["temporary_password"]:
                required_missing.append("temporary_password")
            if required_missing:
                row_errors.append(f"Row {index}: missing {', '.join(required_missing)}.")
                continue

            if not student:
                try:
                    validate_password(cleaned["temporary_password"])
                except ValidationError as exc:
                    row_errors.append(f"Row {index}: temporary_password {' '.join(exc.messages)}")
                    continue

            school_class, _ = SchoolClass.objects.get_or_create(name=cleaned["class_name"])
            session, _ = AcademicSession.objects.get_or_create(name=cleaned["academic_session"])

            if student:
                student.full_name = cleaned["student_name"]
                student.gender = cleaned["gender"]
                student.current_class = school_class
                student.active_session = session
                student.user.username = cleaned["student_id"]
                if cleaned["temporary_password"]:
                    try:
                        validate_password(cleaned["temporary_password"], user=student.user)
                    except ValidationError as exc:
                        row_errors.append(f"Row {index}: temporary_password {' '.join(exc.messages)}")
                        continue
                    student.user.set_password(cleaned["temporary_password"])
                student.user.save()
                student.save()
                updated += 1
            else:
                user = User(username=cleaned["student_id"], role=User.Role.GUARDIAN)
                user.set_password(cleaned["temporary_password"])
                user.save()
                Student.objects.create(
                    user=user,
                    student_id=cleaned["student_id"],
                    full_name=cleaned["student_name"],
                    gender=cleaned["gender"],
                    guardian_name=cleaned["student_name"],
                    guardian_email="",
                    current_class=school_class,
                    active_session=session,
                )
                created += 1

        if row_errors:
            raise ValidationError(row_errors)

    return created, updated


@admin_required
def publications_manage(request):
    form = ResultPublicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        publication, _ = ResultPublication.objects.update_or_create(
            academic_session=form.cleaned_data["academic_session"],
            school_class=form.cleaned_data["school_class"],
            term=form.cleaned_data["term"],
            defaults={"is_published": form.cleaned_data["is_published"], "updated_by": request.user},
        )
        state = "published" if publication.is_published else "unpublished"
        messages.success(request, f"{publication.term} has been {state}.")
        return redirect("publications_manage")

    publications = ResultPublication.objects.select_related("academic_session", "school_class", "updated_by")
    return render(request, "portal/publications.html", {"form": form, "publications": publications})


@admin_required
def publication_toggle(request, publication_id):
    publication = get_object_or_404(ResultPublication, pk=publication_id)
    if request.method == "POST":
        publication.is_published = not publication.is_published
        publication.updated_by = request.user
        publication.save()
        messages.success(request, "Publication status updated.")
    return redirect("publications_manage")


@admin_required
def sessions_manage(request):
    form = AcademicSessionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        session = form.save()
        if session.is_active:
            AcademicSession.objects.exclude(pk=session.pk).update(is_active=False)
        messages.success(request, "Academic session saved.")
        return redirect("sessions_manage")
    return render(request, "portal/sessions.html", {"form": form, "sessions": AcademicSession.objects.all()})


@admin_required
def session_edit(request, session_id):
    session = get_object_or_404(AcademicSession, pk=session_id)
    form = AcademicSessionForm(request.POST or None, instance=session)
    if request.method == "POST" and form.is_valid():
        session = form.save()
        if session.is_active:
            AcademicSession.objects.exclude(pk=session.pk).update(is_active=False)
        messages.success(request, "Academic session updated.")
        return redirect("sessions_manage")
    return render(request, "portal/form.html", {"form": form, "title": "Edit Academic Session"})


@admin_required
def session_delete(request, session_id):
    session = get_object_or_404(AcademicSession, pk=session_id)
    if request.method == "POST":
        try:
            session.delete()
            messages.success(request, "Academic session deleted.")
        except ProtectedError:
            messages.error(request, "This session is linked to students or results and cannot be deleted.")
        return redirect("sessions_manage")
    return render(request, "portal/confirm_delete.html", {"object": session, "title": "Delete Academic Session"})


@admin_required
def classes_manage(request):
    form = SchoolClassForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Class saved.")
        return redirect("classes_manage")
    return render(request, "portal/classes.html", {"form": form, "classes": SchoolClass.objects.all()})


@admin_required
def class_edit(request, class_id):
    school_class = get_object_or_404(SchoolClass, pk=class_id)
    form = SchoolClassForm(request.POST or None, instance=school_class)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Class updated.")
        return redirect("classes_manage")
    return render(request, "portal/form.html", {"form": form, "title": "Edit Class"})


@admin_required
def class_delete(request, class_id):
    school_class = get_object_or_404(SchoolClass, pk=class_id)
    if request.method == "POST":
        try:
            school_class.delete()
            messages.success(request, "Class deleted.")
        except ProtectedError:
            messages.error(request, "This class is linked to students or results and cannot be deleted.")
        return redirect("classes_manage")
    return render(request, "portal/confirm_delete.html", {"object": school_class, "title": "Delete Class"})
