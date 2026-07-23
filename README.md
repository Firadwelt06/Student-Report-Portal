# Secure Student Result Portal

This is a production-minded Django project for a school result portal. Guardians sign in and can view or download only the result PDFs linked to their own child. Administrators manage students, sessions, classes, password resets, and result uploads.

## Recommended Stack

### Backend: Django

Django is the best fit for this portal because authentication, password hashing, sessions, CSRF protection, migrations, forms, file uploads, and admin tooling are built in. Flask is excellent for small APIs and custom systems, but for a school portal you would need to assemble and maintain many security pieces yourself.

| Option | Advantages | Disadvantages |
| --- | --- | --- |
| Django | Secure defaults, mature auth, ORM, migrations, admin, scales well with PostgreSQL/MySQL | More structured; you must learn the Django way |
| Flask | Lightweight, flexible, easy for small apps | You assemble auth, admin, validation, permissions, and structure yourself |

### Database: PostgreSQL or MySQL

For production, use PostgreSQL or MySQL. Since you already have MySQL, this project is MySQL-ready. SQLite is included only as a local learning fallback.

| Option | Advantages | Disadvantages |
| --- | --- | --- |
| SQLite | No setup, good for learning and quick demos | Not ideal for thousands of users or concurrent writes |
| MySQL | You already have it, reliable, widely hosted | Some Django features are smoother on PostgreSQL |
| PostgreSQL | Excellent integrity, indexing, constraints, and production scaling | Requires installing and managing another database |

## Security Decisions

- Passwords are hashed by Django, never stored as plain text.
- Result PDFs are stored under `private_uploads`, not under a public media URL.
- Users cannot fetch PDFs directly by guessing a URL.
- Every PDF request goes through `view_result` or `download_result`.
- Each request checks that the logged-in guardian owns the linked student record.
- Admin pages require an admin or staff account.
- CSRF protection is enabled on forms.
- Production security flags are enabled when `DJANGO_DEBUG=False`.
- Uploaded result files are validated as PDFs.

Recommended improvement for a real school: use guardian email or phone plus a strong password, then add one-time login codes or multi-factor authentication. Student ID plus password is common, but Student IDs can be easy to guess.

## Folder Structure

```text
student_result_portal/
  config/                 Project settings and URL routing
  portal/                 Main app: models, forms, views, URLs, tests
  templates/portal/       HTML templates
  static/portal/          CSS
  static/portal/images/   School logo and image assets
  private_uploads/        Private PDF storage, not publicly served
  manage.py               Django command runner
  requirements.txt        Python dependencies
  .env.example            Environment variable template
```

## Local Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

For first local testing, use the included `.env` with SQLite. Then run:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

After the first setup, your everyday local command is usually only:

```powershell
python manage.py runserver
```

When the project goes online, the hosting platform runs the web server continuously. You do not manually run `runserver`; deployment scripts normally run `python manage.py migrate` and `python manage.py collectstatic --noinput` once per release.

Open:

```text
http://127.0.0.1:8000/
```

Demo accounts:

```text
Admin: admin / AdminPass123!
Guardian: STD-001 / StudentPass123!
```

Change these immediately in any real environment.

## MySQL Setup

Create a MySQL database:

```sql
CREATE DATABASE student_result_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Update `.env`:

```text
DATABASE_ENGINE=mysql
MYSQL_DATABASE=student_result_portal
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

Then run migrations again:

```powershell
python manage.py migrate
```

## How the Core Flow Works

1. An administrator creates a class and academic session.
2. The administrator creates a student.
3. Creating a student also creates a linked guardian login account.
4. The administrator can import many students at once from CSV.
5. The administrator uploads a result PDF for that student, term, class, and session.
6. For faster processing, the administrator can bulk upload all PDFs for a class/term and match them by learner full name.
7. The administrator publishes the matching session/class/term when results are approved.
8. A guardian logs in with the assigned credentials.
9. The dashboard lists only the student's published results.
10. View and download links point to protected Django views.
11. The view checks ownership and publishing status before streaming the PDF.

## Bulk Student CSV Import

Use the admin dashboard's `Import CSV` button. The CSV file must have these exact headings:

```csv
student_id,student_name,gender,class_name,academic_session,temporary_password
```

Example:

```csv
student_id,student_name,gender,class_name,academic_session,temporary_password
STD-001,Ada Johnson,Female,JSS 1A,2026/2027,StudentPass123!
```

Why each heading exists:

- `student_id`: unique login username and permanent school identifier.
- `student_name`: displayed on dashboards and admin searches.
- `gender`: stores the learner's gender for records and reporting.
- `class_name`: creates or links the student to a class.
- `academic_session`: creates or links the student to the active academic year.
- `temporary_password`: creates the initial guardian login password; existing students can leave it blank to keep their current password.

Guardian name and email are now auto-filled for imported records, so the CSV only needs the student-specific details above.

## Result Publishing

Uploaded PDFs are not visible to guardians by default. Go to `Admin -> Publishing`, choose the academic session, class, and term, then mark it published. This allows the school to upload and verify all PDFs before parents can access them.

## Bulk Result PDF Upload

Use `Admin -> Bulk PDFs` when you have all result PDFs ready for a class and term. Select the academic session, class, and term, then choose all PDFs at once.

The current matching rule is:

```text
Student full name in database: Ada Johnson
PDF filename: Ada Johnson.pdf
```

The matching ignores case and punctuation, so `Ada Johnson.pdf`, `ada-johnson.pdf`, and `ADA JOHNSON.pdf` match the same learner. Names must still be unique inside the selected class/session. If two learners have the same full name, use Student ID based filenames in a future importer before uploading.

For best accuracy, keep the PDF names exactly the same as the `full_name` values imported from the student CSV.

## School Logo

The school logo lives here:

```text
static/portal/images/divine_triumph_logo.png
```

For future logo changes, replace that file with a new PNG using the same filename, then run `python manage.py collectstatic --noinput` before deployment.

## Deployment Guidance

For production:

- Use MySQL or PostgreSQL, not SQLite.
- Set `DJANGO_DEBUG=False`.
- Use a long random `DJANGO_SECRET_KEY`.
- Set `DJANGO_ALLOWED_HOSTS` to your real domain.
- Serve the site over HTTPS.
- Store private PDFs outside the public web root.
- Use object storage with signed access for very large deployments.
- Run behind Nginx or a platform proxy.
- Use Gunicorn or another production WSGI server.
- Back up the database and private result PDFs.
- Add monitoring and audit logs for admin actions.

Typical deployment options:

- Render, Railway, Fly.io, DigitalOcean App Platform, or AWS Elastic Beanstalk for managed app hosting.
- DigitalOcean Droplet, AWS EC2, or a school-owned VPS for full control.
- S3-compatible private storage for PDFs when the result library grows.

## Next Production Features

- Email-based password reset for guardians.
- Audit log for admin uploads, deletes, and password resets.
- Bulk result upload matching by Student ID for schools with duplicate learner names.
- Multi-child guardian accounts.
- Rate limiting on login attempts.
- Two-factor authentication for administrators.
