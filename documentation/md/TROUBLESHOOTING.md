# REF-Manager Troubleshooting Guide

## Common Issues and Solutions

---

## Installation Issues

### "No module named 'django'"

**Problem:** Python can't find Django.

**Solution:**
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Then run your command
python manage.py runserver
```

### "Port 8000 already in use"

**Problem:** Another process is using port 8000.

**Solutions:**
```bash
# Option 1: Use different port
python manage.py runserver 8080

# Option 2: Find and kill the process
# Linux/Mac
lsof -i :8000
kill <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "No such table" or migration errors

**Problem:** Database not properly migrated.

**Solution:**
```bash
python manage.py makemigrations
python manage.py migrate
```

If that fails:
```bash
python manage.py migrate --run-syncdb
```

### "Permission denied" on Linux

**Problem:** File permission issues.

**Solution:**
```bash
chmod -R 755 ref-manager/
chmod 644 ref-manager/.env
```

---

## Role and Permission Issues

### "Role 'X' does not exist"

**Problem:** Default roles not created.

**Solution:**
```bash
python manage.py setup_roles
```

### "User has no profile"

**Problem:** UserProfile not created for user.

**Solution:**
```bash
python manage.py setup_roles --create-profiles
```

### User can't access expected features

**Problem:** Wrong role assigned.

**Solution:**
```bash
# Check current roles
python manage.py assign_roles username --show

# Add correct role
python manage.py assign_roles username --add ADMIN
```

---

## Database Issues

### SQLite "database is locked"

**Problem:** SQLite can't handle concurrent access.

**Solutions:**
1. Wait and retry
2. Restart the server
3. For production, switch to PostgreSQL

### PostgreSQL connection refused

**Problem:** Can't connect to PostgreSQL.

**Check:**
```bash
# Is PostgreSQL running?
sudo systemctl status postgresql

# Start if needed
sudo systemctl start postgresql

# Check connection
psql -U refuser -h localhost refmanager
```

### Migration conflicts

**Problem:** Migration files conflict.

**Solution:**
```bash
# Show migration status
python manage.py showmigrations

# Fake problematic migration
python manage.py migrate core 0014 --fake

# Then continue
python manage.py migrate
```

---

## Static Files Issues

### CSS/JS not loading

**Problem:** Static files not collected or served.

**Solutions:**
```bash
# Collect static files
python manage.py collectstatic --clear

# Check STATIC_ROOT setting
# Verify Nginx static location
```

### Images not displaying

**Problem:** Media files not served.

**Check:**
- MEDIA_ROOT configured
- Upload directory exists and is writable
- Nginx media location configured

---

## Import/Export Issues

### CSV import fails

**Problem:** CSV format or encoding issues.

**Solutions:**
- Ensure UTF-8 encoding
- Check column headers match expected names
- Remove BOM if present
- Verify date formats

### BibTeX import fails

**Problem:** Malformed BibTeX entries.

**Solutions:**
- Validate BibTeX syntax
- Check for special characters
- Ensure required fields present

### Excel export error

**Problem:** openpyxl issues.

**Solution:**
```bash
pip install --upgrade openpyxl
```

---

## Performance Issues

### Slow page loads

**Possible causes:**
- Large dataset without pagination
- Missing database indexes
- Debug mode in production

**Solutions:**
```python
# Disable debug
DEBUG = False

# Add database indexes
class Output(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['colleague']),
        ]
```

### High memory usage

**Solutions:**
- Reduce Gunicorn workers
- Add database connection pooling
- Implement pagination

---

## Docker Issues

### Container won't start

**Check logs:**
```bash
docker-compose logs web
docker-compose logs db
```

### Database connection in Docker

**Problem:** Web can't reach database.

**Solution:** Use service name, not localhost:
```python
DB_HOST=db  # Not localhost
```

### Volume permissions

**Problem:** Permission denied in volumes.

**Solution:**
```bash
# Check ownership
docker-compose exec web ls -la /app

# Fix if needed
docker-compose exec web chown -R 1000:1000 /app/media
```

---

## Common Error Messages

### "CSRF verification failed"

**Cause:** CSRF token missing or invalid.

**Solutions:**
- Ensure `{% csrf_token %}` in forms
- Check CSRF_TRUSTED_ORIGINS setting
- Clear browser cookies

### "OperationalError: no such column"

**Cause:** Model changed but not migrated.

**Solution:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### "TemplateDoesNotExist"

**Cause:** Template file missing or wrong path.

**Check:**
- Template file exists
- Template directory in settings
- No typos in template name

### "ImproperlyConfigured"

**Cause:** Settings misconfigured.

**Check:**
- All required settings present
- Environment variables set
- .env file loaded

---

## Getting More Help

### Enable Debug Mode

Temporarily enable for detailed errors:
```python
DEBUG = True
```

### Check Django Logs

```bash
# Console output
python manage.py runserver

# Log file
tail -f /var/log/ref-manager/django.log
```

### Django System Check

```bash
python manage.py check
python manage.py check --deploy  # Production checks
```

### Database Shell

```bash
python manage.py dbshell
python manage.py shell
```

### Collect Debug Information

When reporting issues, include:
1. Python version: `python --version`
2. Django version: `python -c "import django; print(django.VERSION)"`
3. Error message (full traceback)
4. Steps to reproduce
5. Relevant configuration

---

## Still Stuck?

1. Search existing GitHub issues
2. Check Django documentation
3. Contact: george.tsoulas@york.ac.uk
4. Open new GitHub issue with details
