# REF Manager - Complete Installation Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Initial Setup](#initial-setup)
5. [Troubleshooting](#troubleshooting)
6. [Backup and Maintenance](#backup-and-maintenance)

---

## System Requirements

### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10/11
- **Python**: 3.9 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 500MB minimum for application and database
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)

### Required Software
- Python 3.9+
- pip (Python package manager)
- Git (optional, for version control)
- LaTeX distribution (optional, for compiling reports)

---

## Installation Steps

### Step 1: Install Python

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

#### Windows
1. Download Python from https://www.python.org/downloads/
2. Run installer and check "Add Python to PATH"
3. Verify installation: `python --version`

### Step 2: Download REF Manager

#### Option A: From Archive
```bash
# If you have a zip/tar archive
unzip ref-manager.zip
cd ref-manager
```

#### Option B: Copy from Existing Installation
```bash
# Copy the entire project directory
cp -r /path/to/existing/ref-manager ~/ref-manager
cd ~/ref-manager
```

### Step 3: Create Virtual Environment

```bash
# Navigate to project directory
cd ref-manager

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

### Step 4: Install Dependencies

```bash
# Ensure pip is up to date
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

**Expected packages:**
- Django==4.2.7
- python-dotenv==1.0.0
- Pillow
- django-crispy-forms==2.1
- crispy-bootstrap4==2024.10
- openpyxl

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cat > .env << 'EOF'
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (SQLite - default)
# For PostgreSQL, uncomment and configure:
# DB_NAME=ref_manager
# DB_USER=postgres
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=5432
EOF
```

**Generate a secure SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and replace `your-secret-key-here-change-this` in `.env`

### Step 6: Initialize Database

```bash
# Create database migrations
python manage.py makemigrations core
python manage.py makemigrations reports

# Apply migrations
python manage.py migrate

# Verify database creation
ls -lh db.sqlite3
```

### Step 7: Create Superuser Account

```bash
python manage.py createsuperuser
```

Enter:
- Username (e.g., admin)
- Email (optional)
- Password (enter twice)

### Step 8: Create Media Directories

```bash
# Create directories for file uploads
mkdir -p media/uploads media/tmp
```

### Step 9: Test Installation

```bash
# Start development server
python manage.py runserver

# Server should start at: http://127.0.0.1:8000/
```

Open your browser and visit:
- **Application**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

Login with the superuser credentials you created.

---

## Configuration

### Database Configuration

#### SQLite (Default - Development)
No additional configuration needed. Database file: `db.sqlite3`

#### PostgreSQL (Production Recommended)

1. **Install PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
```

2. **Create Database and User:**
```bash
sudo -u postgres psql

CREATE DATABASE ref_manager;
CREATE USER ref_user WITH PASSWORD 'your_password';
ALTER ROLE ref_user SET client_encoding TO 'utf8';
ALTER ROLE ref_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ref_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ref_manager TO ref_user;
\q
```

3. **Update `config/settings.py`:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ref_manager'),
        'USER': os.getenv('DB_USER', 'ref_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

4. **Install PostgreSQL driver:**
```bash
pip install psycopg2-binary
```

5. **Update .env file** with your PostgreSQL credentials

### Email Configuration (Optional)

For sending notifications and reminders:

```python
# Add to config/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

---

## Initial Setup

### 1. Access Admin Panel

1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. Configure initial data

### 2. Add Staff Members

**Option A: Via Web Interface**
1. Click "Staff" in navigation
2. Click "Add Staff Member"
3. Fill in details
4. Save

**Option B: Via Import**
1. Click "Import Data"
2. Download "Colleagues Template"
3. Fill in Excel/CSV
4. Upload

### 3. Add Research Outputs

**Option A: Via Web Interface**
1. Click "Outputs" → "Add Output"
2. Select staff member
3. Fill in publication details
4. Save

**Option B: Via Import**
1. Import staff first (outputs need existing staff)
2. Download "Outputs Template"
3. Fill in details
4. Upload

### 4. Add Critical Friends

1. Click "Critical Friends" → "Add Critical Friend"
2. Enter external reviewer details
3. Save

---

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -ti :8000

# Kill the process
kill $(lsof -ti :8000)

# Or use a different port
python manage.py runserver 8080
```

#### Module Not Found Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

#### Database Migrations Failed
```bash
# Delete existing migrations
rm -rf core/migrations/0*.py
rm -rf reports/migrations/0*.py
rm db.sqlite3

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

#### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput
```

#### Permission Denied Errors
```bash
# Fix file permissions
chmod -R 755 media/
chmod -R 755 static/
```

---

## Backup and Maintenance

### Database Backup

#### SQLite
```bash
# Backup database
cp db.sqlite3 backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Restore database
cp backups/db_20241021_120000.sqlite3 db.sqlite3
```

#### PostgreSQL
```bash
# Backup
pg_dump ref_manager > backups/ref_backup_$(date +%Y%m%d).sql

# Restore
psql ref_manager < backups/ref_backup_20241021.sql
```

### Automated Backup Script

Create `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sqlite3" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Make executable and run:
```bash
chmod +x backup.sh
./backup.sh
```

### Regular Maintenance

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Check for Django security issues
python manage.py check --deploy

# Clear old sessions
python manage.py clearsessions

# Optimize database (SQLite)
python manage.py sqlflush
```

---

## Production Deployment

### Security Checklist

1. **Set DEBUG to False** in `.env`
```bash
DEBUG=False
```

2. **Generate New SECRET_KEY**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. **Configure ALLOWED_HOSTS**
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

4. **Use PostgreSQL** instead of SQLite

5. **Collect Static Files**
```bash
python manage.py collectstatic
```

6. **Use HTTPS** with proper SSL certificates

### Deployment Options

#### Option 1: Using Gunicorn + Nginx

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

#### Option 2: Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t ref-manager .
docker run -p 8000:8000 ref-manager
```

---

## System Administration

### Creating Additional Users

```bash
# Via command line
python manage.py shell

from django.contrib.auth.models import User
user = User.objects.create_user('username', 'email@example.com', 'password')
user.save()
```

### User Permissions

Users can be assigned to groups:
- **Department Admin**: Can add/edit all data
- **Staff**: Can view and edit own outputs
- **Reviewer**: Can view and comment on outputs

---

## Support and Documentation

For additional help:
- Check Django documentation: https://docs.djangoproject.com/
- Report issues to your system administrator
- Review application logs in console output

---

## Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate

# Start server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Backup database
cp db.sqlite3 backups/db_$(date +%Y%m%d).sqlite3

# Update dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

---

**Installation complete! Your REF Manager is ready to use.** 🎉
