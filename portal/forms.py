from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import AcademicSession, ResultDocument, ResultPublication, SchoolClass, Student, User


class PortalLoginForm(AuthenticationForm):
    username = forms.CharField(label="Student ID or Admin Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class StudentForm(forms.ModelForm):
    initial_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Required when creating a new student. Use a temporary password and force reset operationally.",
    )

    class Meta:
        model = Student
        fields = [
            "student_id",
            "full_name",
            "guardian_name",
            "guardian_email",
            "current_class",
            "active_session",
        ]

    def __init__(self, *args, **kwargs):
        self.instance_user = kwargs.pop("instance_user", None)
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["initial_password"].help_text = "Leave blank to keep the current password."

    def clean_initial_password(self):
        password = self.cleaned_data.get("initial_password")
        if not self.instance.pk and not password:
            raise ValidationError("A temporary password is required for new students.")
        if password:
            validate_password(password)
        return password

    def save(self, commit=True):
        student = super().save(commit=False)
        password = self.cleaned_data.get("initial_password")

        if not student.pk:
            user = User(username=student.student_id, role=User.Role.GUARDIAN, email=student.guardian_email)
            user.set_password(password)
            if commit:
                user.save()
            student.user = user
        else:
            user = student.user
            user.username = student.student_id
            user.email = student.guardian_email
            if password:
                user.set_password(password)
            if commit:
                user.save()

        if commit:
            student.save()
        return student


class ResultDocumentForm(forms.ModelForm):
    class Meta:
        model = ResultDocument
        fields = ["student", "academic_session", "school_class", "term", "pdf"]


class MultiplePDFInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class BulkResultUploadForm(forms.Form):
    academic_session = forms.ModelChoiceField(queryset=AcademicSession.objects.all())
    school_class = forms.ModelChoiceField(queryset=SchoolClass.objects.all())
    term = forms.CharField(max_length=30, help_text="Example: First Term")
    pdf_files = forms.FileField(
        label="Result PDFs",
        widget=MultiplePDFInput(attrs={"multiple": True, "accept": "application/pdf"}),
        help_text="Select all PDFs for this class and term. Each filename should match the learner's full name.",
    )

    def clean_pdf_files(self):
        files = self.files.getlist("pdf_files")
        if not files:
            raise ValidationError("Select at least one PDF file.")
        if len(files) > 300:
            raise ValidationError("Upload 300 PDFs or fewer at a time.")
        for pdf_file in files:
            if not pdf_file.name.lower().endswith(".pdf"):
                raise ValidationError(f"{pdf_file.name} is not a PDF.")
            header = pdf_file.read(4)
            pdf_file.seek(0)
            if header != b"%PDF":
                raise ValidationError(f"{pdf_file.name} does not appear to be a valid PDF.")
        return files


class StudentCSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label="Student CSV file",
        help_text="Upload a UTF-8 CSV file with the required student import headings.",
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if not csv_file.name.lower().endswith(".csv"):
            raise ValidationError("Only CSV files are allowed.")
        if csv_file.size > 2 * 1024 * 1024:
            raise ValidationError("CSV file is too large. Keep imports under 2MB per upload.")
        return csv_file


class ResultPublicationForm(forms.ModelForm):
    class Meta:
        model = ResultPublication
        fields = ["academic_session", "school_class", "term", "is_published"]


class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ["name", "is_active"]


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name"]


class AdminPasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("new_password")
        confirm = cleaned.get("confirm_password")
        if password and confirm and password != confirm:
            raise ValidationError("Passwords do not match.")
        if password:
            validate_password(password)
        return cleaned
