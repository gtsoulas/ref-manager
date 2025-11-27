# REF-Manager Technical Documentation

## Developer and Administrator Reference

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Project Structure](#2-project-structure)
3. [Database Schema](#3-database-schema)
4. [Configuration](#4-configuration)
5. [Management Commands](#5-management-commands)
6. [API Reference](#6-api-reference)
7. [Deployment](#7-deployment)
8. [Security](#8-security)
9. [Maintenance](#9-maintenance)
10. [Development](#10-development)

---

## 1. Architecture Overview

### Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 4.2, Python 3.10+ |
| Database | SQLite (dev), PostgreSQL (prod) |
| Frontend | Bootstrap 4, Chart.js |
| Forms | django-crispy-forms |
| Export | openpyxl, custom LaTeX |
| Server | Gunicorn, Nginx |
| Container | Docker |

### Application Structure

```
┌─────────────────────────────────────────┐
│              Web Browser                 │
├─────────────────────────────────────────┤
│              Nginx (HTTPS)               │
├─────────────────────────────────────────┤
│              Gunicorn (WSGI)             │
├─────────────────────────────────────────┤
│           Django Application             │
│  ┌─────────┬─────────┬─────────┐        │
│  │  Core   │ Reports │ Access  │        │
│  │  App    │   App   │ Control │        │
│  └─────────┴─────────┴─────────┘        │
├─────────────────────────────────────────┤
│         PostgreSQL Database              │
└─────────────────────────────────────────┘
```

---

## 2. Project Structure

```
ref-manager/
├── config/                 # Django project settings
│   ├── __init__.py
│   ├── settings.py         # Main settings
│   ├── urls.py             # Root URL configuration
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
│
├── core/                   # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View controllers
│   ├── forms.py            # Form definitions
│   ├── urls.py             # URL routing
│   ├── admin.py            # Django admin config
│   ├── mixins.py           # View mixins
│   ├── decorators.py       # Permission decorators
│   ├── models_access_control.py  # RBAC models
│   ├── views_export.py     # Export views
│   ├── views_user_management.py  # User management
│   ├── excel_import.py     # Import utilities
│   ├── output_comparison.py # Duplicate detection
│   ├── templates/          # HTML templates
│   ├── templatetags/       # Custom template tags
│   ├── management/         # Management commands
│   └── migrations/         # Database migrations
│
├── reports/                # Reporting module
│   ├── views.py            # Report views
│   ├── latex_generator.py  # LaTeX generation
│   ├── excel_export.py     # Excel export
│   ├── portfolio_optimizer.py  # Portfolio metrics
│   └── templates/          # Report templates
│
├── templates/              # Base templates
│   ├── base.html           # Base template
│   └── core/               # Core templates
│
├── static/                 # Static assets
│   ├── css/
│   ├── js/
│   └── images/
│
├── documentation/          # Documentation
│   ├── md/                 # Markdown
│   ├── latex/              # LaTeX
│   └── pdf/                # PDF
│
├── docker-compose.yml      # Docker configuration
├── Dockerfile              # Docker image
├── requirements.txt        # Python dependencies
├── manage.py               # Django management
└── env.example             # Environment template
```

---

## 3. Database Schema

### Core Models

#### Colleague
```python
class Colleague(models.Model):
    user = models.OneToOneField(User)
    staff_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=20)
    fte = models.DecimalField(max_digits=3, decimal_places=2)
    contract_type = models.CharField(max_length=50)
    employment_status = models.CharField(max_length=10)
    employment_end_date = models.DateField(null=True)
    colleague_category = models.CharField(max_length=50)
    unit_of_assessment = models.CharField(max_length=100)
    is_returnable = models.BooleanField(default=True)
```

#### Output
```python
class Output(models.Model):
    colleague = models.ForeignKey(Colleague)
    title = models.CharField(max_length=500)
    publication_type = models.CharField(max_length=1)
    publication_year = models.IntegerField()
    publication_venue = models.CharField(max_length=300)
    doi = models.CharField(max_length=200)
    all_authors = models.TextField()
    author_position = models.IntegerField()
    uoa = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    
    # Quality ratings
    quality_rating_internal = models.CharField(max_length=2)
    quality_rating_external = models.CharField(max_length=2)
    quality_rating_self = models.CharField(max_length=2)
    quality_rating_average = models.CharField(max_length=2)
    
    # Risk fields
    content_risk_score = models.DecimalField(max_digits=3, decimal_places=2)
    timeline_risk_score = models.DecimalField(max_digits=3, decimal_places=2)
    overall_risk_score = models.DecimalField(max_digits=3, decimal_places=2)
    oa_compliance_risk = models.BooleanField(default=False)
```

#### Access Control Models
```python
class Role(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('OBSERVER', 'Observer'),
        ('INTERNAL_PANEL', 'Internal Panel'),
        ('COLLEAGUE', 'Colleague'),
    ]
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    permissions = models.JSONField()

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    roles = models.ManyToManyField(Role)
```

#### REFSubmission
```python
class REFSubmission(models.Model):
    name = models.CharField(max_length=200)
    uoa = models.CharField(max_length=100)
    submission_year = models.IntegerField(default=2029)
    outputs = models.ManyToManyField(Output, through='SubmissionOutput')
    
    # Metrics
    portfolio_quality_score = models.DecimalField()
    portfolio_risk_score = models.DecimalField()
    representativeness_score = models.DecimalField()
    equality_score = models.DecimalField()
    gender_balance_score = models.DecimalField()
```

---

## 4. Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Secret key | Required |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost` |
| `DB_ENGINE` | Database engine | `sqlite3` |
| `DB_NAME` | Database name | `db.sqlite3` |
| `DB_USER` | Database user | - |
| `DB_PASSWORD` | Database password | - |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |

### settings.py Configuration

```python
# Database (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'refmanager'),
        'USER': os.getenv('DB_USER', 'refuser'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Security (Production)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

---

## 5. Management Commands

### setup_roles
Create default roles and user profiles.

```bash
# Create roles only
python manage.py setup_roles

# Create profiles for existing users
python manage.py setup_roles --create-profiles

# Make superusers administrators
python manage.py setup_roles --superusers-admin

# All options
python manage.py setup_roles --create-profiles --superusers-admin
```

### assign_roles
Manage user role assignments.

```bash
# List all users and roles
python manage.py assign_roles --list

# Show user details
python manage.py assign_roles username --show

# Add role
python manage.py assign_roles username --add ADMIN

# Add multiple roles
python manage.py assign_roles username --add OBSERVER INTERNAL_PANEL

# Set exact roles
python manage.py assign_roles username --set ADMIN

# Remove role
python manage.py assign_roles username --remove OBSERVER

# Clear all roles
python manage.py assign_roles username --clear
```

### calculate_risks
Recalculate risk scores for all outputs.

```bash
python manage.py calculate_risks
```

---

## 6. API Reference

### View Mixins

```python
from core.mixins import (
    AdminRequiredMixin,      # Require admin role
    OutputAccessMixin,       # Filter outputs by permission
    CanEditMixin,            # Check edit permission
    ObserverOrAdminMixin,    # Require observer or admin
)

class MyView(AdminRequiredMixin, ListView):
    model = Output
```

### Decorators

```python
from core.decorators import (
    admin_required,          # Function view: admin only
    permission_required,     # Specific permission
    output_edit_permission,  # Can edit specific output
)

@admin_required
def admin_view(request):
    pass

@permission_required('can_export_data')
def export_view(request):
    pass
```

### Template Tags

```html
{% load ref_permissions %}

{% if output|can_edit:user.ref_profile %}
    <a href="{% url 'output-edit' output.pk %}">Edit</a>
{% endif %}

{% if user.ref_profile|has_permission:'can_export_data' %}
    <a href="{% url 'export' %}">Export</a>
{% endif %}

{% user_role_badges user.ref_profile %}
{% role_summary %}
```

### UserProfile Properties

```python
profile = request.user.ref_profile

# Role checks
profile.is_admin
profile.is_observer
profile.is_panel_member
profile.is_colleague

# Permissions
profile.can_view_all_outputs
profile.can_edit_any_output
profile.can_rate_assigned
profile.can_export_data

# Role management
profile.has_role('ADMIN')
profile.add_role('OBSERVER')
profile.remove_role('INTERNAL_PANEL')
```

---

## 7. Deployment

### Docker Deployment

```bash
# Build and start
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Set up roles
docker-compose exec web python manage.py setup_roles --create-profiles --superusers-admin
```

### Traditional Deployment

```bash
# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Configure Gunicorn
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 60

# Configure Nginx (see nginx/conf.d/)
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name ref.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name ref.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 8. Security

### Production Checklist

- [ ] DEBUG = False
- [ ] Secure SECRET_KEY
- [ ] HTTPS enforced
- [ ] Database password set
- [ ] ALLOWED_HOSTS configured
- [ ] CSRF protection enabled
- [ ] Session cookies secure
- [ ] File upload limits set

### Recommended Settings

```python
# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 9. Maintenance

### Database Backup

```bash
# PostgreSQL backup
pg_dump -U refuser refmanager > backup.sql

# Restore
psql -U refuser refmanager < backup.sql
```

### Log Management

Log locations:
- Application: `/var/log/ref-manager/gunicorn.log`
- Nginx: `/var/log/nginx/`
- PostgreSQL: `/var/log/postgresql/`

### Performance Tuning

PostgreSQL settings:
```ini
shared_buffers = 256MB
effective_cache_size = 768MB
work_mem = 16MB
maintenance_work_mem = 128MB
```

---

## 10. Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/gtsoulas/ref-manager.git
cd ref-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python manage.py test

# Start development server
python manage.py runserver
```

### Code Style

- Follow PEP 8
- Use meaningful variable names
- Document functions and classes
- Keep functions small and focused

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add my feature"

# Push and create PR
git push origin feature/my-feature
```

---

## Appendix: URL Routes

### Core URLs

| URL | Name | View |
|-----|------|------|
| `/` | dashboard | Dashboard |
| `/colleagues/` | colleague_list | Colleague list |
| `/outputs/` | output_list | Output list |
| `/critical-friends/` | critical_friend_list | Critical friend list |
| `/internal-panel/` | internal_panel_list | Internal panel list |
| `/tasks/` | task_list | Task list |

### Reports URLs

| URL | Name | View |
|-----|------|------|
| `/reports/` | reports:home | Reports home |
| `/reports/risk-dashboard/` | reports:risk-dashboard | Risk dashboard |
| `/reports/submissions/` | reports:submission-list | Submissions |

### Management URLs

| URL | Name | View |
|-----|------|------|
| `/manage/users/` | user-list | User list |
| `/manage/users/<id>/roles/` | user-role-edit | Edit roles |
