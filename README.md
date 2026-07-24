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

## Managing Newsletters

Newsletters appear on the public home page, student dashboards, and admin dashboards. To create or edit a newsletter:

1. Go to `/admin/`
2. Click **Newsletters**
3. Click **Add Newsletter** to create a new one
4. Fill in:
   - **Title**: e.g. "Term 1 Results Now Available"
   - **Academic Session**: e.g. "2026/2027"
   - **Summary**: Brief text for the dashboard card preview
   - **Body**: Full newsletter content (paragraphs separated by blank lines)
   - **Featured Image** (optional): A PNG or JPG image for the newsletter
   - **Published**: Tick to display it on the portal
5. Click **Save**

The latest published newsletter will automatically appear on:
- Public home page (before login)
- Student dashboard (after login)
- Admin dashboard

---

## Deployment: Online Setup

### Pre-Deployment Checklist

Before going live, ensure you have:

- [ ] Production database (PostgreSQL or MySQL) created and accessible
- [ ] A hosting platform account (Railway, Render, Fly.io, DigitalOcean, AWS, etc.)
- [ ] A custom domain name (optional but recommended)
- [ ] HTTPS certificate (most platforms provide this automatically)
- [ ] Email credentials for password resets (optional but recommended)

### Environment Variables (.env)

Create a `.env` file in the project root with these values:

```text
# Core Security
DJANGO_SECRET_KEY=your_very_long_random_secret_key_here_min_50_chars
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-app.railway.app

# Database (PostgreSQL example)
DATABASE_URL=postgresql://username:password@host:5432/database_name

# Or MySQL
# DATABASE_ENGINE=mysql
# MYSQL_DATABASE=student_result_portal
# MYSQL_USER=admin_user
# MYSQL_PASSWORD=strong_password
# MYSQL_HOST=your-db-host.com
# MYSQL_PORT=3306

# Email (for password resets and feedback)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-school@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_or_smtp_token
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# CSRF & CORS
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

⚠️ **Never commit `.env` to version control. Add it to `.gitignore`.**

For `DJANGO_SECRET_KEY`, generate a strong random key:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

For Gmail SMTP, use an [App Password](https://myaccount.google.com/apppasswords) instead of your real Gmail password.

### Option 1: Deploy on Railway (Recommended for Quick Setup)

1. **Sign up** at [railway.app](https://railway.app)
2. **Connect your GitHub repository** (or upload the project)
3. **Create a new project**
4. **Add services:**
   - PostgreSQL database (or MySQL)
   - Python web service (deploy from this repository)
5. **Add environment variables** from your `.env` file
6. **Deploy**

Railway automatically:
- Runs migrations on deploy
- Collects static files
- Handles HTTPS
- Provides a subdomain URL (e.g. `your-app-abc123.railway.app`)

### Option 2: Deploy on Render.com

1. **Sign up** at [render.com](https://render.com)
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Configure build and start commands:**
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
5. **Add environment variables** from your `.env` file
6. **Connect a PostgreSQL database** (or add MySQL credentials)
7. **Deploy**

### Option 3: Deploy on AWS Elastic Beanstalk

1. **Install AWS CLI and EB CLI**
2. **Initialize EB project:**
   ```bash
   eb init -p python-3.9 student-result-portal --region us-east-1
   ```
3. **Create environment:**
   ```bash
   eb create production --database --database.engine postgres --database.size db.t3.micro
   ```
4. **Set environment variables:**
   ```bash
   eb setenv DJANGO_DEBUG=False DJANGO_SECRET_KEY=... DATABASE_URL=...
   ```
5. **Deploy:**
   ```bash
   eb deploy
   ```

### Option 4: Deploy on DigitalOcean App Platform

1. **Sign up** at [digitalocean.com](https://digitalocean.com)
2. **Create a new App** and connect your GitHub repository
3. **DigitalOcean will auto-detect** the Python environment
4. **Add a Managed PostgreSQL database**
5. **Set environment variables** in the app config
6. **Deploy**

### Post-Deployment Steps

After your app is live:

1. **Run migrations on the production database:**
   ```bash
   python manage.py migrate
   ```

2. **Create a superuser (admin account):**
   ```bash
   python manage.py createsuperuser
   ```

3. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Seed demo data (optional, for testing):**
   ```bash
   python manage.py seed_demo
   ```

5. **Change the demo admin password** in `/admin/` immediately

6. **Set up a custom domain** (if using a subdomain from your platform)

7. **Enable HTTPS** (automatic on most platforms)

### Production Security Checklist

- [ ] `DJANGO_DEBUG = False` in production
- [ ] `DJANGO_SECRET_KEY` is long and random
- [ ] Database credentials are environment variables, not hardcoded
- [ ] `DJANGO_ALLOWED_HOSTS` includes your domain and www variant
- [ ] `CSRF_TRUSTED_ORIGINS` is set correctly
- [ ] HTTPS is enforced (add `SECURE_SSL_REDIRECT = True` to settings if needed)
- [ ] Email backend is configured for password resets
- [ ] Backups are scheduled for your database
- [ ] Media uploads (newsletters, etc.) are served securely
- [ ] Private PDFs remain outside the public web root
- [ ] Admin credentials are strong and changed from demo defaults
- [ ] Logging and monitoring are enabled for errors and access

### Scaling for Large Deployments

If your school grows and the app serves thousands of students:

1. **Use object storage** (AWS S3, DigitalOcean Spaces) for media files:
   ```bash
   pip install django-storages boto3
   ```

2. **Use a CDN** (Cloudflare, AWS CloudFront) to cache static files and images

3. **Set up database replication** for read-heavy loads

4. **Enable caching** (Redis) for session and query results

5. **Use a background job queue** (Celery + Redis) for bulk email and imports

6. **Monitor with APM** (New Relic, DataDog, Sentry) for errors and performance

### Backup & Recovery

Set up automated backups for your database and media files:

- **Database**: Most platforms offer automated daily backups. Verify in your platform dashboard.
- **Media files**: Set up scheduled uploads to S3 or a backup service.
- **Code**: Keep your GitHub repository as your primary backup.

Test restores regularly to ensure you can recover from data loss.

### Monitoring & Maintenance

After deployment:

- Monitor server logs daily for errors
- Check admin dashboard for failed login attempts
- Back up the database weekly
- Review slow queries and optimize if needed
- Keep Django and dependencies updated with security patches
- Test password resets and data exports monthly

---

## Development

### Running Tests

```powershell
python manage.py test portal.tests
```

### Linting & Code Style

Consider adding:
- `flake8` for style checks
- `black` for code formatting
- `isort` for import sorting

### Database Migrations

After changing models:

```powershell
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

### "No module named 'django'" after installing requirements

Make sure you activated the virtual environment:

```powershell
./.venv/Scripts/Activate.ps1
```

### "Could not find config for 'default' in settings.STORAGES"

This error occurs when uploading newsletter images. Make sure `STORAGES` in `config/settings.py` includes both a `"default"` backend for media uploads and a `"staticfiles"` backend for static files (this should be configured in the current version).

### Database migrations failed

```powershell
python manage.py migrate --fake-initial
```

Use `--fake-initial` only if the database already has the schema but migrations weren't tracked.

### Can't log in

1. Check the `.env` file is correct
2. Verify the database is running and accessible
3. Run `python manage.py migrate` to ensure tables exist
4. Reset the admin password: `python manage.py changepassword admin`

---

## Next Production Features

- Email-based password reset for guardians.
- Audit log for admin uploads, deletes, and password resets.
- Bulk result upload matching by Student ID for schools with duplicate learner names.
- Multi-child guardian accounts.
- Rate limiting on login attempts.
- Two-factor authentication for administrators.
