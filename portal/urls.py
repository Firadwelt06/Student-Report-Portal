from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.PortalLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("results/<int:result_id>/view/", views.view_result, name="view_result"),
    path("results/<int:result_id>/download/", views.download_result, name="download_result"),
    path("admin-portal/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-portal/students/add/", views.student_create, name="student_create"),
    path("admin-portal/students/<int:student_id>/edit/", views.student_edit, name="student_edit"),
    path("admin-portal/students/<int:student_id>/delete/", views.student_delete, name="student_delete"),
    path("admin-portal/students/<int:student_id>/reset-password/", views.reset_student_password, name="reset_student_password"),
    path("admin-portal/students/import-csv/", views.student_csv_import, name="student_csv_import"),
    path("admin-portal/results/upload/", views.result_upload, name="result_upload"),
    path("admin-portal/results/bulk-upload/", views.bulk_result_upload, name="bulk_result_upload"),
    path("admin-portal/results/publications/", views.publications_manage, name="publications_manage"),
    path("admin-portal/results/publications/<int:publication_id>/toggle/", views.publication_toggle, name="publication_toggle"),
    path("admin-portal/sessions/", views.sessions_manage, name="sessions_manage"),
    path("admin-portal/sessions/<int:session_id>/edit/", views.session_edit, name="session_edit"),
    path("admin-portal/sessions/<int:session_id>/delete/", views.session_delete, name="session_delete"),
    path("admin-portal/classes/", views.classes_manage, name="classes_manage"),
    path("admin-portal/classes/<int:class_id>/edit/", views.class_edit, name="class_edit"),
    path("admin-portal/classes/<int:class_id>/delete/", views.class_delete, name="class_delete"),
    path("feedback/", views.submit_feedback, name="submit_feedback"),
    path("newsletters/", views.NewsletterListView.as_view(), name="newsletter_list"),
    path("newsletters/<slug:slug>/", views.NewsletterDetailView.as_view(), name="newsletter_detail"),
]
