# REF-Manager Troubleshooting Guide

## Common Issues and Solutions v4.0

---

## Table of Contents

1. [Installation Issues](#1-installation-issues)
2. [Database Issues](#2-database-issues)
3. [DOI Auto-Fetch Issues](#3-doi-auto-fetch-issues)
4. [O/S/R Rating Issues](#4-osr-rating-issues)
5. [Import Issues](#5-import-issues)
6. [Server Deployment Issues](#6-server-deployment-issues)
7. [Performance Issues](#7-performance-issues)

---

## 1. Installation Issues

### "No module named 'requests'"

The requests library is required for DOI auto-fetch.

**Solution:**
```bash
pip install requests
# Or if using system Python:
pip install requests --break-system-packages
```

### "ModuleNotFoundError: No module named 'crispy_forms'"

**Solution:**
```bash
pip install django-crispy-forms crispy-bootstrap5
```

### Virtual environment not activating

**Solution:**
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# If permission denied
chmod +x venv/bin/activate
```

---

## 2. Database Issues

### "table already exists" during migration

Your database tables exist but migrations are out of sync.

**Solution:**
```bash
# Option 1: Fake initial migration
python manage.py migrate --fake-initial

# Option 2: Fake all core migrations
python manage.py migrate core --fake

# Then apply new migrations
python manage.py makemigrations core
python manage.py migrate
```

### "no such column" error

Model fields don't match database schema.

**Solution:**
```bash
# Check migration status
python manage.py showmigrations core

# Create missing migration
python manage.py makemigrations core

# Apply it
python manage.py migrate
```

### PostgreSQL connection refused

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start if stopped
sudo systemctl start postgresql

# Check connection settings in .env
DATABASE_URL=postgres://user:password@localhost:5432/ref_manager
```

---

## 3. DOI Auto-Fetch Issues

### "DOI not found in OpenAlex database"

The DOI might be new or incorrectly formatted.

**Solutions:**

1. **Check DOI format** - Should start with `10.`
   ```
   ✓ 10.1038/nature12373
   ✓ doi:10.1038/nature12373
   ✓ https://doi.org/10.1038/nature12373
   ✗ nature12373
   ```

2. **Test the API directly:**
   ```bash
   curl "https://api.openalex.org/works/doi:10.1038/nature12373"
   ```

3. **Very recent DOIs** may not be indexed yet - wait 1-2 weeks

### "Connection timeout" or network errors

**Solutions:**

1. **Check internet connection**
   ```bash
   curl -I https://api.openalex.org
   ```

2. **Check firewall/proxy** - OpenAlex API must be accessible

3. **University network** may block external APIs - try from different network

### OA status not populating

The JavaScript might not be finding the form field.

**Solution:**
1. Open browser DevTools (F12)
2. Check Console for errors
3. Verify field ID is `id_oa_status`

---

## 4. O/S/R Rating Issues

### Ratings not saving

**Solutions:**

1. **Check field validation** - Values must be 0.00-4.00
2. **Check form errors** - Look for red validation messages
3. **Verify migration ran:**
   ```bash
   python manage.py showmigrations core | grep osr
   ```

### Average not calculating

The average properties require all three components.

**Check in Django shell:**
```python
python manage.py shell
from core.models import Output
o = Output.objects.get(pk=1)
print(o.originality_internal, o.significance_internal, o.rigour_internal)
print(o.osr_internal_average)
```

### Old star ratings showing

Template may be cached or not updated.

**Solution:**
```bash
# Clear template cache
python manage.py clear_cache

# Collect static files
python manage.py collectstatic --clear --noinput

# Restart server
sudo systemctl restart gunicorn-ref-manager
```

---

## 5. Import Issues

### CSV encoding errors

**Solution:**
- Save CSV as UTF-8 (without BOM)
- Or use UTF-8-BOM encoding
- Avoid special characters in filenames

### Bulk import skipping all rows

**Check:**
1. CSV column headers match expected names
2. DOIs are valid format (for Smart mode)
3. Staff IDs match existing colleagues

**Expected columns:**
```
doi,title,publication_year,publication_venue,all_authors,publication_type,staff_id
```

### "Duplicate detected" for all rows

Disable duplicate checking or clear existing data.

**Solution:**
- Uncheck "Skip duplicates" option
- Or delete existing outputs first

---

## 6. Server Deployment Issues

### 502 Bad Gateway

Gunicorn is not running or crashed.

**Solution:**
```bash
# Check status
sudo systemctl status gunicorn-ref-manager

# View logs
sudo journalctl -u gunicorn-ref-manager -n 50

# Restart
sudo systemctl restart gunicorn-ref-manager
```

### Static files not loading (404)

**Solution:**
```bash
# Collect static files
cd /var/www/ref-manager
source venv/bin/activate
python manage.py collectstatic --noinput

# Check Nginx config
sudo nginx -t

# Verify static directory
ls -la /var/www/ref-manager/static/

# Restart Nginx
sudo systemctl restart nginx
```

### CSRF verification failed

**Solution:**
Add your domain to settings:
```python
CSRF_TRUSTED_ORIGINS = [
    'https://your-domain.ac.uk',
    'https://www.your-domain.ac.uk',
]
```

### Permission denied errors

**Solution:**
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/ref-manager

# Fix permissions
sudo chmod -R 755 /var/www/ref-manager
sudo chmod -R 775 /var/www/ref-manager/media
sudo chmod -R 775 /var/www/ref-manager/logs
```

---

## 7. Performance Issues

### Slow page loads

**Solutions:**

1. **Enable database indexes:**
   ```python
   # In models.py
   class Meta:
       indexes = [
           models.Index(fields=['doi']),
           models.Index(fields=['title']),
       ]
   ```

2. **Use select_related:**
   ```python
   Output.objects.select_related('colleague').all()
   ```

3. **Enable caching:**
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
       }
   }
   ```

### High memory usage

**Solution:**
Reduce Gunicorn workers:
```python
# gunicorn.conf.py
workers = 2  # Instead of 4
```

---

## Log Files

| Log | Location |
|-----|----------|
| Django | `/var/www/ref-manager/logs/django.log` |
| Gunicorn | `/var/www/ref-manager/logs/gunicorn-*.log` |
| Nginx access | `/var/log/nginx/ref-manager-access.log` |
| Nginx error | `/var/log/nginx/ref-manager-error.log` |
| System | `journalctl -u gunicorn-ref-manager` |

---

## Health Check Commands

```bash
# Check all services
sudo systemctl status gunicorn-ref-manager nginx postgresql

# Test database
python manage.py dbshell

# Check for issues
python manage.py check --deploy

# Verify migrations
python manage.py showmigrations
```

---

## Getting Help

If you can't resolve an issue:

1. Check the logs for specific error messages
2. Search GitHub Issues
3. Contact: george.tsoulas@york.ac.uk

Include:
- Error message (full traceback)
- Steps to reproduce
- Django/Python version
- Operating system
