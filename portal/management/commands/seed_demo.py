from django.core.management.base import BaseCommand

from portal.models import AcademicSession, Newsletter, SchoolClass, Student, User


class Command(BaseCommand):
    help = "Create demo admin, session, class, and one student account."

    def handle(self, *args, **options):
        session, _ = AcademicSession.objects.get_or_create(name="2026/2027", defaults={"is_active": True})
        school_class, _ = SchoolClass.objects.get_or_create(name="JSS 1A")

        admin, created = User.objects.get_or_create(username="admin", defaults={"role": User.Role.ADMIN, "is_staff": True, "is_superuser": True})
        if created:
            admin.set_password("AdminPass123!")
            admin.save()

        student_user, created = User.objects.get_or_create(username="STD-001", defaults={"role": User.Role.GUARDIAN, "email": "guardian@example.com"})
        if created:
            student_user.set_password("StudentPass123!")
            student_user.save()

        Student.objects.get_or_create(
            user=student_user,
            defaults={
                "student_id": "STD-001",
                "full_name": "Ada Johnson",
                "gender": "Female",
                "guardian_name": "Mrs. Johnson",
                "guardian_email": "guardian@example.com",
                "current_class": school_class,
                "active_session": session,
            },
        )

        Newsletter.objects.get_or_create(
            title="Welcome to Divine Triumph Newsletter",
            defaults={
                "slug": "welcome-newsletter",
                "academic_session": session.name,
                "summary": "Stay up to date with school announcements and news from Divine Triumph International School.",
                "body": "Welcome to the portal! This newsletter introduces the student dashboard and latest school news.",
                "published": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data ready. Admin: admin / AdminPass123!, Student: STD-001 / StudentPass123!"))
