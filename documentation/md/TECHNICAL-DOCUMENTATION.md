# REF-Manager Technical Documentation

## Developer and Administrator Reference v4.0

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Installation](#2-installation)
3. [Server Deployment](#3-server-deployment)
4. [Database Schema](#4-database-schema)
5. [API Reference](#5-api-reference)
6. [Configuration](#6-configuration)
7. [Management Commands](#7-management-commands)
8. [Backup & Recovery](#8-backup--recovery)

---

## 1. Architecture Overview

### Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Django 4.2 LTS |
| Language | Python 3.10+ |
| Database | SQLite (dev) / PostgreSQL 15 (prod) |
| Web Server | Nginx |
| WSGI Server | Gunicorn |
| Frontend | Bootstrap 5, Chart.js |

### Application Structure

```
ref-manager/
├── config/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                # Main application
│   ├── models.py        # Data models
│   ├── views.py         # View functions
│   ├── forms.py         # Form definitions
│   ├── admin.py         # Admin configuration
│   ├── urls.py          # URL routing
│   └── templates/       # HTML templates
├── static/              # Static files
├── media/               # User uploads
├── manage.py
└── requirements.txt
```

---

## 2. Installation

### Development Setup

```bash
# Clone repository
git clone https://github.com/gtsoulas/ref-manager.git
cd ref-manager

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install requests  # For DOI auto-fetch

# Configure environment
cp env.example .env
# Edit .env as needed

# Initialize database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Setup roles
python manage.py setup_roles --create-profiles --superusers-admin

# Run development server
python manage.py runserver
```

### Dependencies

```txt
Django>=4.2,<5.0
psycopg2-binary>=2.9.0
gunicorn>=21.0.0
django-crispy-forms>=2.0
crispy-bootstrap5>=0.7
openpyxl>=3.1.0
python-docx>=0.8.11
bibtexparser>=1.4.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## 3. Server Deployment

### Ubuntu Server Setup

#### System Packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    python3.12 python3.12-venv python3.12-dev \
    postgresql postgresql-contrib \
    nginx certbot python3-certbot-nginx \
    git
```

#### PostgreSQL Database

```bash
sudo -u postgres psql

CREATE DATABASE ref_manager;
CREATE USER ref_user WITH PASSWORD 'secure_password';
ALTER ROLE ref_user SET client_encoding TO 'utf8';
ALTER ROLE ref_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ref_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ref_manager TO ref_user;
\q
```

#### Application Setup

```bash
# Create directory
sudo mkdir -p /var/www/ref-manager
sudo chown $USER:$USER /var/www/ref-manager
cd /var/www/ref-manager

# Clone and setup
git clone https://github.com/gtsoulas/ref-manager.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary requests

# Create directories
mkdir -p static media logs
```

#### Environment Configuration

Create `/var/www/ref-manager/.env`:

```bash
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.ac.uk

DATABASE_URL=postgres://ref_user:password@localhost:5432/ref_manager

STATIC_ROOT=/var/www/ref-manager/static
MEDIA_ROOT=/var/www/ref-manager/media

CSRF_TRUSTED_ORIGINS=https://your-domain.ac.uk
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Gunicorn Configuration

Create `/var/www/ref-manager/gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
timeout = 120
errorlog = "/var/www/ref-manager/logs/gunicorn-error.log"
accesslog = "/var/www/ref-manager/logs/gunicorn-access.log"
loglevel = "info"
```

#### Systemd Service

Create `/etc/systemd/system/gunicorn-ref-manager.service`:

```ini
[Unit]
Description=Gunicorn daemon for REF-Manager
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ref-manager
ExecStart=/var/www/ref-manager/venv/bin/gunicorn \
    --config /var/www/ref-manager/gunicorn.conf.py \
    config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-ref-manager
sudo systemctl start gunicorn-ref-manager
```

#### Nginx Configuration

Create `/etc/nginx/sites-available/ref-manager`:

```nginx
server {
    listen 80;
    server_name your-domain.ac.uk;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.ac.uk;

    ssl_certificate /etc/letsencrypt/live/your-domain.ac.uk/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.ac.uk/privkey.pem;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/ref-manager/static/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/ref-manager/media/;
    }

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/ref-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### SSL Certificate

```bash
sudo certbot --nginx -d your-domain.ac.uk
```

---

## 4. Database Schema

### Core Models (v4.0)

#### Output Model - New Fields

```python
# O/S/R Self-Assessment
originality_self = DecimalField(max_digits=3, decimal_places=2)
significance_self = DecimalField(max_digits=3, decimal_places=2)
rigour_self = DecimalField(max_digits=3, decimal_places=2)

# O/S/R Internal Panel
originality_internal = DecimalField(max_digits=3, decimal_places=2)
significance_internal = DecimalField(max_digits=3, decimal_places=2)
rigour_internal = DecimalField(max_digits=3, decimal_places=2)

# O/S/R External (Critical Friend)
originality_external = DecimalField(max_digits=3, decimal_places=2)
significance_external = DecimalField(max_digits=3, decimal_places=2)
rigour_external = DecimalField(max_digits=3, decimal_places=2)

# OA Compliance
acceptance_date = DateField(null=True)
deposit_date = DateField(null=True)
embargo_end_date = DateField(null=True)
oa_status = CharField(choices=OA_STATUS_CHOICES)
oa_exception = CharField(choices=OA_EXCEPTION_CHOICES)

# Narrative Statements
double_weighting_statement = TextField(max_length=2000)
interdisciplinary_statement = TextField(max_length=3500)
```

#### O/S/R Properties

```python
@property
def osr_self_average(self):
    """Average of self-assessment O/S/R ratings"""
    
@property
def osr_internal_average(self):
    """Average of internal panel O/S/R ratings"""
    
@property
def osr_external_average(self):
    """Average of critical friend O/S/R ratings"""
    
@property
def osr_combined_average(self):
    """Average across all sources"""
    
@property
def osr_combined_average_no_self(self):
    """Average of internal + external only"""
```

---

## 5. API Reference

### DOI Metadata Endpoint

**URL**: `/outputs/fetch-doi/`

**Method**: GET

**Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `doi` | string | DOI to look up |

**Response**:
```json
{
  "success": true,
  "data": {
    "title": "Paper Title",
    "publication_year": 2024,
    "publication_venue": "Journal Name",
    "volume": "12",
    "issue": "3",
    "pages": "123-145",
    "all_authors": "Smith, J., Jones, A.",
    "citation_count": 42,
    "is_oa": true,
    "oa_status": "gold",
    "publication_type": "A"
  }
}
```

**Error Response**:
```json
{
  "error": "DOI not found in OpenAlex database"
}
```

---

## 6. Configuration

### Key Settings

```python
# REF Configuration
REF_SUBMISSION_YEAR = 2029
REF_CENSUS_DATE = "2029-07-31"
DEFAULT_UOA = "26 - Modern Languages and Linguistics"

# OA Compliance
OA_DEPOSIT_DEADLINE_DAYS = 92  # 3-month rule

# Rating Scale
RATING_SCALE_MIN = 0.00
RATING_SCALE_MAX = 4.00

# File Uploads
MAX_UPLOAD_SIZE = 52428800  # 50 MB
```

---

## 7. Management Commands

| Command | Description |
|---------|-------------|
| `setup_roles` | Create user roles and permissions |
| `assign_roles` | Assign roles to users |
| `import_outputs` | Bulk import from CSV |
| `export_outputs` | Export to CSV/Excel |
| `calculate_risk` | Recalculate risk scores |
| `check_oa_compliance` | Verify OA compliance |

### Examples

```bash
# Setup roles
python manage.py setup_roles --create-profiles --superusers-admin

# Assign admin role
python manage.py assign_roles username --add ADMIN

# Import outputs
python manage.py import_outputs --file outputs.csv --mode hybrid

# Check OA compliance
python manage.py check_oa_compliance --report
```

---

## 8. Backup & Recovery

### Database Backup

```bash
# PostgreSQL
pg_dump -U ref_user ref_manager > backup_$(date +%Y%m%d).sql

# Restore
psql -U ref_user ref_manager < backup_20251203.sql
```

### Automated Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/ref-manager"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database
pg_dump -U ref_user ref_manager > "$BACKUP_DIR/db_$DATE.sql"

# Media files
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /var/www/ref-manager/media/

# Cleanup (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /var/www/ref-manager/backup.sh
```

---

## Support

- **Author**: George Tsoulas
- **Email**: george.tsoulas@york.ac.uk
- **GitHub**: https://github.com/gtsoulas/ref-manager
