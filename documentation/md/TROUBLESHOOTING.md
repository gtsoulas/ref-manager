# REF Manager v2.0 - Troubleshooting Guide

**Problem Solving and Solutions**

**Version:** 2.0.0  
**Last Updated:** November 3, 2025

---

## 📋 Quick Problem Finder

**Installation Issues**
- [Python version problems](#python-version-issues)
- [Package installation failures](#package-installation-failures)
- [Virtual environment errors](#virtual-environment-errors)

**Runtime Errors**
- [Server won't start](#server-wont-start)
- [Database errors](#database-errors)
- [Permission denied](#permission-denied-errors)

**Feature-Specific**
- [CSV import failures](#csv-import-issues)
- [Excel export problems](#excel-export-issues)
- [PDF upload issues](#pdf-upload-issues)
- [Login problems](#authentication-issues)

**Performance**
- [Slow loading](#performance-issues)
- [Database queries](#slow-database-queries)

---

## 🔧 Installation Issues

### Python Version Issues

**Problem:** Wrong Python version or Python 3.13 compatibility errors

**Error Messages:**
```
TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and 'float'
```

**Solution:**
1. Check Python version:
   ```bash
   python3 --version
   ```
   Should be 3.10 or higher.

2. If you have Python 3.13, the decimal issue is fixed in v2.0. Update to latest code.

3. For decimal errors in `required_outputs`:
   ```python
   # In models.py, change:
   return self.fte * 2.5
   # To:
   return float(self.fte) * 2.5
   ```

### Package Installation Failures

**Problem:** `pip install` fails

**Error Messages:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solutions:**

**For Python 3.13:**
```bash
pip install --break-system-packages -r requirements.txt
```

**For permission errors:**
```bash
pip install --user -r requirements.txt
```

**For specific package failures:**
```bash
# Update pip first
pip install --upgrade pip

# Install packages one by one to identify problem
pip install Django==4.2.0
pip install django-crispy-forms==2.0
# etc.
```

**For PostgreSQL adapter issues:**
```bash
# Install PostgreSQL development files first
sudo apt-get install libpq-dev python3-dev

# Then install psycopg2
pip install psycopg2-binary
```

### Virtual Environment Errors

**Problem:** Virtual environment not activating

**Solutions:**

**Linux/macOS:**
```bash
# Create fresh venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
# Create fresh venv
rmdir /s venv
python -m venv venv
venv\Scripts\activate
```

**If activation still fails:**
```bash
# Check Python venv module is installed
python3 -m pip install virtualenv

# Use virtualenv instead
virtualenv venv
source venv/bin/activate
```

---

## 🚀 Runtime Errors

### Server Won't Start

**Problem:** `python manage.py runserver` fails

**Error 1: Port already in use**
```
Error: That port is already in use.
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 PID

# Or use different port
python manage.py runserver 8001
```

**Error 2: Import errors**
```
ModuleNotFoundError: No module named 'crispy_forms'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

**Error 3: Settings errors**
```
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.
```

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Add to .env file
echo "SECRET_KEY=generated-key-here" >> .env
```

### Database Errors

**Problem:** Database migrations fail

**Error: No such table**
```
django.db.utils.OperationalError: no such table: core_colleague
```

**Solution:**
```bash
# Run migrations
python manage.py migrate

# If that fails, try:
python manage.py migrate --run-syncdb
```

**Error: Migration conflicts**
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:**
```bash
# Show migrations
python manage.py showmigrations

# Fake problematic migration
python manage.py migrate core --fake 0001

# Then run normally
python manage.py migrate
```

**Error: PostgreSQL connection refused**
```
FATAL: password authentication failed for user "ref_manager_user"
```

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start if needed
sudo systemctl start postgresql

# Reset password
sudo -u postgres psql
ALTER USER ref_manager_user WITH PASSWORD 'new_password';
\q

# Update .env file with new password
```

### Permission Denied Errors

**Problem:** Can't access files or database

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/path/to/file'
```

**Solutions:**

**For database file:**
```bash
# SQLite database
chmod 664 db.sqlite3
chmod 775 .
```

**For media files:**
```bash
chmod -R 755 media/
```

**For logs:**
```bash
mkdir -p logs
chmod 775 logs
```

---

## 📊 Feature-Specific Issues

### CSV Import Issues

**Problem:** CSV import fails or gives errors

**Error 1: Encoding problems**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**Solution:**
```bash
# Save CSV as UTF-8 in Excel:
# File → Save As → CSV UTF-8 (Comma delimited) (.csv)

# Or convert existing file:
iconv -f ISO-8859-1 -t UTF-8 oldfile.csv > newfile.csv
```

**Error 2: Missing required columns**
```
ValidationError: Missing required columns: title, all_authors
```

**Solution:**
- Download CSV template from import page
- Ensure all required columns present:
  - title
  - all_authors
  - publication_venue
  - publication_type
  - publication_date
  - quality_rating
  - author_email
  - uoa
  - ref_eligible

**Error 3: Date format errors**
```
ValidationError: Invalid date format
```

**Solution:**
- Use YYYY-MM-DD format: 2025-01-15
- Not DD/MM/YYYY or MM/DD/YYYY

**Error 4: Email not matching colleague**
```
Warning: No colleague found with email: x@example.com
```

**Solution:**
- Ensure colleague exists in system first
- Check email spelling matches exactly
- Or add colleague before import

**Error 5: Quality rating invalid**
```
ValidationError: Quality rating must be 0, 1, 2, 3, or 4
```

**Solution:**
- Use numbers only: 0, 1, 2, 3, or 4
- 0 = Unclassified
- 4 = 4* (World-Leading)

### Excel Export Issues

**Problem:** Excel export fails or links don't work

**Error 1: Export button does nothing**
```
Check browser console for JavaScript errors
```

**Solution:**
```bash
# Reinstall openpyxl
pip install --force-reinstall openpyxl

# Check version
pip show openpyxl
# Should be 3.1.2+
```

**Error 2: Links not clickable**

**Solution:**
- Ensure PDFs are uploaded for outputs
- Check PDF files are accessible
- Verify file paths in media directory

**Error 3: File download fails**

**Solution:**
```bash
# Check disk space
df -h

# Check permissions
ls -la media/pdfs/

# Check media URL in settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MEDIA_ROOT)
>>> print(settings.MEDIA_URL)
```

### PDF Upload Issues

**Problem:** Can't upload PDF files

**Error 1: File too large**
```
RequestDataTooBig: The request's size exceeds the maximum allowed
```

**Solution:**
```python
# In settings.py, add:
DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520  # 20MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 20971520  # 20MB
```

**For Nginx:**
```nginx
# In nginx config
client_max_body_size 20M;
```

**Error 2: Invalid file type**
```
ValidationError: Only PDF files allowed
```

**Solution:**
- Ensure file extension is .pdf
- Check file is actually PDF (not renamed)
- Maximum 20MB per file

**Error 3: Upload directory not writable**
```
PermissionError: [Errno 13] Permission denied: '/path/to/media/pdfs/'
```

**Solution:**
```bash
mkdir -p media/pdfs
chmod -R 755 media
chown -R your-username:your-username media
```

### Authentication Issues

**Problem:** Can't log in

**Error 1: Forgot password**

**Solution:**
```bash
# Reset password via command line
python manage.py changepassword username
```

**Error 2: User doesn't exist**

**Solution:**
```bash
# Create new user
python manage.py createsuperuser

# Or create via shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('username', 'email@example.com', 'password')
```

**Error 3: Session expired**

**Solution:**
- Just log in again
- To extend sessions, in settings.py:
```python
SESSION_COOKIE_AGE = 86400  # 24 hours
```

---

## ⚡ Performance Issues

### Slow Loading

**Problem:** Pages load slowly

**Diagnosis:**
```python
# Enable Django Debug Toolbar
pip install django-debug-toolbar

# Add to INSTALLED_APPS in settings.py
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

# Add to MIDDLEWARE
MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Add to urls.py
import debug_toolbar
urlpatterns = [
    # ...
    path('__debug__/', include(debug_toolbar.urls)),
]

# Set INTERNAL_IPS
INTERNAL_IPS = ['127.0.0.1']
```

**Solutions:**

**1. Database query optimization:**
```python
# Use select_related for foreign keys
colleagues = Colleague.objects.select_related('user').all()

# Use prefetch_related for reverse relationships
colleagues = Colleague.objects.prefetch_related('outputs').all()
```

**2. Add database indexes:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**3. Enable caching:**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Slow Database Queries

**Problem:** Database queries taking too long

**Diagnosis:**
```bash
# Enable query logging
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

**Solutions:**

**1. Reduce number of queries:**
```python
# Bad - N+1 queries
for colleague in Colleague.objects.all():
    print(colleague.user.username)

# Good - 2 queries
for colleague in Colleague.objects.select_related('user'):
    print(colleague.user.username)
```

**2. Use aggregation:**
```python
from django.db.models import Count

# Bad
for colleague in Colleague.objects.all():
    count = colleague.outputs.count()

# Good
colleagues = Colleague.objects.annotate(
    output_count=Count('outputs')
)
```

**3. Switch to PostgreSQL for large datasets**

---

## 🗂️ Data Issues

### Category Field Inconsistencies

**Problem:** Categories stored with both hyphens and underscores

**Error:**
```
Colleague shows 'non-independent' in database but 'non_independent' in code
```

**Solution:**
```bash
# Run data migration
python manage.py shell

from core.models import Colleague

# Fix hyphenated entries
colleagues = Colleague.objects.filter(colleague_category='non-independent')
for c in colleagues:
    c.colleague_category = 'non_independent'
    c.save()

print(f"Fixed {colleagues.count()} colleagues")
```

### Missing Dropdowns

**Problem:** Colleague categories or status not showing in forms

**Solution:**

**1. Check model choices are correct:**
```python
# In models.py
COLLEAGUE_CATEGORY_CHOICES = [
    ('non_independent', 'Non-Independent Researcher'),
    # Ensure underscore, not hyphen
]
```

**2. Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**3. Clear browser cache:**
- Ctrl+Shift+R (hard refresh)
- Or clear all cache

**4. Collect static files:**
```bash
python manage.py collectstatic --clear --noinput
```

---

## 🔄 Systemd Service Issues

**Problem:** Systemd service won't start

**Error:**
```
Job for ref-manager.service failed
```

**Diagnosis:**
```bash
# Check service status
sudo systemctl status ref-manager

# View logs
sudo journalctl -u ref-manager -n 50
```

**Common Issues:**

**1. Wrong username in service file**
```ini
# /etc/systemd/system/ref-manager.service
[Service]
User=CORRECT_USERNAME  # Must match your actual username
```

**2. Wrong paths**
```ini
WorkingDirectory=/home/CORRECT_USERNAME/ref-project-app/ref-manager
ExecStart=/home/CORRECT_USERNAME/ref-project-app/ref-manager/venv/bin/gunicorn ...
```

**3. Virtual environment not activated**
```ini
Environment="PATH=/home/USERNAME/ref-project-app/ref-manager/venv/bin"
```

**Fix and reload:**
```bash
# Edit service file
sudo nano /etc/systemd/system/ref-manager.service

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart ref-manager

# Check status
sudo systemctl status ref-manager
```

---

## 📝 Template Errors

**Problem:** Template syntax errors

**Error:**
```
TemplateSyntaxError: Invalid block tag
```

**Common causes:**

**1. Unbalanced tags:**
```html
<!-- Bad -->
{% if condition %}
    <div>Content</div>
<!-- Missing {% endif %} -->

<!-- Good -->
{% if condition %}
    <div>Content</div>
{% endif %}
```

**2. Missing template tag load:**
```html
<!-- Bad -->
{{ value|custom_filter }}

<!-- Good -->
{% load custom_filters %}
{{ value|custom_filter }}
```

**3. Wrong quote types:**
```html
<!-- Bad -->
href="{% url 'core:view_name" %}

<!-- Good -->
href="{% url 'core:view_name' %}"
```

---

## 🛠️ Development Tools

### Django Shell Issues

**Problem:** Can't access Django shell

**Solution:**
```bash
# Standard shell
python manage.py shell

# Enhanced shell (install ipython)
pip install ipython
python manage.py shell
```

### Missing Admin Styling

**Problem:** Admin panel has no CSS

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT setting
python manage.py shell
>>> from django.conf import settings
>>> print(settings.STATIC_ROOT)

# Restart server
sudo systemctl restart ref-manager
```

---

## 📞 Getting Additional Help

### Information to Include When Seeking Help

When reporting issues, include:

**1. System Information:**
```bash
# Python version
python3 --version

# Django version
python manage.py version

# OS information
uname -a
```

**2. Error Message:**
- Full error traceback
- When error occurs
- Steps to reproduce

**3. Recent Changes:**
- What was changed before error
- New packages installed
- Configuration changes

**4. Logs:**
```bash
# Application logs
tail -n 100 logs/django.log

# System service logs
sudo journalctl -u ref-manager -n 100

# Nginx logs (if applicable)
sudo tail -n 100 /var/log/nginx/error.log
```

### Diagnostic Commands

```bash
# Check Django installation
python manage.py check

# Check deployment settings
python manage.py check --deploy

# Show migrations
python manage.py showmigrations

# Show database state
python manage.py dbshell
.tables  # (in SQLite)
\dt      # (in PostgreSQL)

# Test database connection
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("Connected!")
```

---

## 🔍 Common Error Messages Index

| Error | Section |
|-------|---------|
| TypeError: Decimal and float | [Python 3.13](#python-version-issues) |
| Port already in use | [Server won't start](#server-wont-start) |
| No such table | [Database errors](#database-errors) |
| Permission denied | [Permission errors](#permission-denied-errors) |
| UnicodeDecodeError | [CSV import](#csv-import-issues) |
| File too large | [PDF upload](#pdf-upload-issues) |
| Invalid date format | [CSV import](#csv-import-issues) |
| TemplateSyntaxError | [Template errors](#template-errors) |
| Service failed | [Systemd](#systemd-service-issues) |
| Missing static files | [Missing admin styling](#missing-admin-styling) |

---

**Version:** 2.0.0  
**Last Updated:** November 3, 2025  
**Maintained by:** George Tsoulas

For additional support, see complete documentation suite or contact system administrator.
