# REF Manager v2.0 - Quick Start Guide

**Get up and running in 10 minutes!**

**Version:** 2.0.0  
**Last Updated:** November 3, 2025

---

## 📋 Prerequisites

Before you start, ensure you have:
- Python 3.10 or higher installed
- Terminal/Command Prompt access
- Internet connection
- 500MB free disk space

**Quick Check:**
```bash
python3 --version  # Should show 3.10 or higher
```

---

## 🚀 Installation (10 Minutes)

### Step 1: Download and Setup (2 minutes)

```bash
# Create project directory
mkdir -p ~/ref-project-app
cd ~/ref-project-app

# If using Git
git clone https://github.com/yourusername/ref-manager.git
cd ref-manager

# OR extract ZIP file if downloaded
# unzip ref-manager.zip
# cd ref-manager
```

### Step 2: Create Virtual Environment (1 minute)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# You should see (venv) in your prompt
```

### Step 3: Install Dependencies (3 minutes)

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# If on Python 3.13 and getting errors:
pip install --break-system-packages -r requirements.txt
```

**What gets installed:**
- Django 4.2+ (web framework)
- django-crispy-forms (beautiful forms)
- openpyxl (Excel export)  ⭐ NEW
- gunicorn (production server)
- psycopg2-binary (PostgreSQL support)

### Step 4: Configure Environment (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Generate a secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env file
nano .env  # or use any text editor
```

**Minimum .env configuration:**
```env
SECRET_KEY=paste-the-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 5: Initialize Database (2 minutes)

```bash
# Create database tables
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Enter username, email, and password when prompted
```

### Step 6: Start the Server (1 minute)

```bash
# Run development server
python manage.py runserver

# Server should start at http://127.0.0.1:8000
```

**🎉 Congratulations! Your REF Manager is running!**

Open your browser and go to: **http://localhost:8000**

---

## 📱 First Steps After Installation

### 1. Log In (1 minute)

1. Open http://localhost:8000
2. Click **"Login"** in the top right
3. Enter your superuser credentials
4. You'll see the dashboard

### 2. Explore the Dashboard (2 minutes)

The dashboard shows:
- **Submission Statistics**: Output counts and quality profile
- **Staff Summary**: Current and former colleagues
- **Review Progress**: Critical Friends and Internal Panel
- **Task Overview**: ⭐ NEW - Urgent and overdue tasks
- **Recent Activity**: Latest changes

### 3. Add Your First Colleague (3 minutes)

1. Click **"Colleagues"** in navigation
2. Click **"Add Colleague"** button
3. Fill in:
   - First name, Last name
   - Email
   - Unit of Assessment
   - FTE (Full-Time Equivalent, e.g., 1.0)
   - **Employment Status**: Current ⭐ NEW
   - **Category**: Choose appropriate type ⭐ NEW
4. Click **"Save"**

**⭐ NEW Categories in v2.0:**
- Independent Researcher
- Non-Independent Researcher (for post-docs)
- Post-Doctoral Researcher
- Research Assistant
- Academic Staff
- Support Staff
- Co-author (External)

### 4. Add Your First Output (5 minutes)

1. Click **"Outputs"** in navigation
2. Click **"Add Output"** button
3. Fill in essential fields:
   - **Title**: Full publication title
   - **Authors**: All author names
   - **Publication Venue**: Journal/conference name
   - **Publication Type**: Article, Book, Chapter, etc.
   - **Publication Date**
   - **Quality Rating**: 4*, 3*, 2*, 1*, or Unclassified
   - **Author (Lead)**: Select from colleagues
   - **REF Eligible**: Yes/No
   - **Unit of Assessment**
4. Optional: Upload PDF
5. Click **"Save"**

### 5. Try the New Features (5 minutes)

#### ⭐ Create a Task
1. Click **"Tasks"** in navigation
2. Click **"Create Task"**
3. Fill in:
   - Title
   - Category (e.g., "Submission", "Administrative")
   - Priority (Low, Medium, High, Urgent)
   - Due Date
   - Description
4. Click **"Save"**

#### ⭐ Set Up Internal Panel
1. Click **"Internal Panel"** in navigation
2. Click **"Add Panel Member"**
3. Select a colleague
4. Choose role (Chair, Member, Specialist)
5. Click **"Save"**

#### ⭐ Try CSV Import
1. Click **"Outputs"** → **"Import"**
2. Download the CSV template
3. Fill in output data
4. Upload CSV file
5. Review and confirm import

---

## 🎯 Daily Workflow

### Typical REF Manager Day:

**Morning (5 minutes):**
1. Check dashboard for urgent tasks
2. Review overdue reviews
3. Check recent activity

**During the Day:**
- Add new outputs as they're published
- Update colleague information
- Assign papers for review
- Track review progress
- Complete tasks

**Weekly (15 minutes):**
- Review quality profile
- Check submission progress
- Update request status
- Generate reports

**Monthly (30 minutes):**
- Full review progress audit
- Update staff status (current/former)
- Export data for meetings
- Generate comprehensive reports

---

## 🛠️ Running as Background Service

### Option 1: Using Screen (Simplest)

```bash
# Install screen
sudo apt-get install screen

# Start screen session
screen -S ref-manager

# Run server
cd ~/ref-project-app/ref-manager
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Detach: Press Ctrl+A, then D

# Reattach later
screen -r ref-manager
```

### Option 2: Using systemd (Production)

Create service file:
```bash
sudo nano /etc/systemd/system/ref-manager.service
```

```ini
[Unit]
Description=REF Manager Django Application
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/ref-project-app/ref-manager
Environment="PATH=/home/YOUR_USERNAME/ref-project-app/ref-manager/venv/bin"
ExecStart=/home/YOUR_USERNAME/ref-project-app/ref-manager/venv/bin/gunicorn \
    --workers 3 \
    --bind 0.0.0.0:8000 \
    ref_manager.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

**Replace YOUR_USERNAME with your actual username!**

Enable and start:
```bash
sudo systemctl enable ref-manager
sudo systemctl start ref-manager
sudo systemctl status ref-manager
```

**Manage the service:**
```bash
# Start
sudo systemctl start ref-manager

# Stop
sudo systemctl stop ref-manager

# Restart (after code changes)
sudo systemctl restart ref-manager

# Check status
sudo systemctl status ref-manager

# View logs
sudo journalctl -u ref-manager -f
```

---

## ⚡ Quick Commands Reference

### Daily Commands

```bash
# Start server (development)
python manage.py runserver

# Start server (accessible from other computers)
python manage.py runserver 0.0.0.0:8000

# Access Django shell
python manage.py shell

# Create backup
cp db.sqlite3 backups/db.sqlite3.$(date +%Y%m%d)
```

### Admin Tasks

```bash
# Create new user
python manage.py createsuperuser

# Change password
python manage.py changepassword username

# Collect static files (production)
python manage.py collectstatic --noinput
```

### Database Tasks

```bash
# Create migrations (after model changes)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Access database directly
python manage.py dbshell
```

---

## 🔧 Common Tasks

### Export Review Assignments ⭐ NEW

1. Go to **"Export"** → **"Assignments"**
2. Select filters:
   - Reviewer type (Internal Panel / Critical Friends)
   - Specific reviewer
   - Output author
   - Status
3. Click **"Export to Excel"**
4. Opens Excel with clickable links to papers
5. Send to reviewers via email

### Import Outputs from CSV ⭐ NEW

1. Go to **"Outputs"** → **"Import"**
2. Download CSV template
3. Fill in columns:
   - title, authors, publication_venue, publication_date
   - publication_type, quality_rating, doi, url
   - author_email (links to colleague)
4. Upload CSV
5. Review validation results
6. Confirm import

### Mark Staff as Former ⭐ NEW

1. Go to **"Colleagues"** → Select colleague
2. Click **"Edit"**
3. Change **"Employment Status"** to "Former"
4. Set **"Employment End Date"**
5. Click **"Save"**
6. Former staff data is preserved but filtered from dropdowns

### Manage Internal Panel ⭐ NEW

**Add Panel Member:**
1. **"Internal Panel"** → **"Add Member"**
2. Select colleague
3. Choose role (Chair, Member, Specialist, External Liaison)
4. Set expertise area
5. Save

**Assign Review:**
1. **"Outputs"** → Select output → **"Assign Internal"**
2. Select panel member
3. Set priority and due date
4. Add notes
5. Save

**Track Progress:**
- Dashboard shows Internal Panel statistics
- Click **"Internal Panel"** to see all assignments
- Filter by status, member, quality

### Task Management ⭐ NEW

**Create Task:**
1. **"Tasks"** → **"Create Task"**
2. Enter title and description
3. Select category and priority
4. Set due date
5. Assign to user (optional)
6. Save

**Complete Task:**
1. **"Tasks"** → Select task
2. Click **"Mark Complete"**
3. Confirm

**View Urgent Tasks:**
- Dashboard shows urgent tasks widget
- Red badges indicate overdue tasks
- Click to view details

---

## 🆘 Quick Fixes for Common Issues

### Issue: Can't log in

**Solution:**
```bash
# Reset password
python manage.py changepassword yourusername
```

### Issue: Page not loading / CSS not working

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Restart server
# Press Ctrl+C, then run again
python manage.py runserver
```

### Issue: "No such table" errors

**Solution:**
```bash
# Run migrations
python manage.py migrate
```

### Issue: Python 3.13 compatibility

**Error:** `TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and 'float'`

**Solution:** Already fixed in v2.0 code. If you see this:
```python
# In models.py, change:
return self.fte * 2.5
# To:
return float(self.fte) * 2.5
```

### Issue: CSV Import fails

**Solutions:**
- Ensure file is UTF-8 encoded
- Check required columns are present
- Verify email addresses match existing colleagues
- Remove special characters from data
- Check file size < 5MB

### Issue: Excel Export not working

**Solution:**
```bash
# Reinstall openpyxl
pip install --force-reinstall openpyxl
```

### Issue: Can't upload PDFs

**Solution:**
```bash
# Check media directory exists
mkdir -p media/pdfs
chmod 755 media
```

### Issue: Server won't start

**Check:**
```bash
# Is port 8000 already in use?
lsof -i :8000
# Kill process if needed
kill -9 PID

# Or use different port
python manage.py runserver 8001
```

### Issue: Permission denied errors

**Solution:**
```bash
# Fix permissions
chmod -R 755 ~/ref-project-app/ref-manager
chmod 664 db.sqlite3
```

---

## 📊 What's New in v2.0

### Major Additions

✅ **Employment Status Tracking**
- Current vs Former staff
- Employment end dates
- Historical data preservation

✅ **Enhanced Categories**
- 9 distinct colleague categories
- Non-independent researcher option
- Better classification for REF

✅ **Internal Panel System**
- Separate from Critical Friends
- Internal reviewer management
- Dashboard statistics

✅ **Task Management**
- Complete task tracking
- Priorities and deadlines
- Categories and status

✅ **CSV Import**
- Bulk output import
- Colleague import
- Validation and error reporting

✅ **Excel Export**
- Export review assignments
- Clickable paper links
- Color-coded formatting

✅ **Enhanced Requests**
- Mark as completed
- Delete with confirmation
- Better status tracking

✅ **Dashboard Updates**
- Internal Panel widget
- Task overview widget
- Enhanced statistics

---

## 📚 Next Steps

**After Quick Start:**

1. **Read the User Guide** (`USER-GUIDE.md`)
   - Detailed feature documentation
   - Best practices
   - Advanced workflows

2. **Check Technical Documentation** (`TECHNICAL-DOCUMENTATION.md`)
   - System architecture
   - Development guide
   - API reference

3. **Review Troubleshooting Guide** (`TROUBLESHOOTING.md`)
   - Detailed problem solving
   - Performance optimization
   - Security considerations

4. **Read the Changelog** (`CHANGELOG.md`)
   - Version history
   - All changes and improvements
   - Migration notes

---

## 💡 Pro Tips

1. **Regular Backups**: Back up database daily
   ```bash
   cp db.sqlite3 backups/db.sqlite3.$(date +%Y%m%d)
   ```

2. **Use Categories**: Properly categorize colleagues for better reporting

3. **Track Everything**: Use tasks to track all REF activities

4. **Export Often**: Export data regularly for meetings and reports

5. **Former Staff**: Don't delete former staff - mark as "Former" instead

6. **CSV Import**: Use CSV import for bulk data entry - much faster!

7. **Excel Export**: Export assignments with links to send to reviewers

8. **Dashboard**: Check dashboard daily for urgent items

9. **Internal vs External**: Use Internal Panel for university reviewers, Critical Friends for external

10. **Quality Ratings**: Update ratings as papers are evaluated

---

## 🎓 Learning Resources

**Quick Videos (if available):**
- Getting Started (5 min)
- Adding Outputs (3 min)
- Managing Reviews (5 min)
- New v2.0 Features (10 min)

**Documentation:**
- Full README: Comprehensive system documentation
- User Guide: Feature-by-feature guide
- Technical Docs: For administrators and developers

**Support:**
- Email: [your-support-email]
- Office Hours: [schedule]
- Documentation: All docs in `/docs` folder

---

## ✅ Checklist

Use this checklist to ensure proper setup:

**Installation:**
- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] Superuser created
- [ ] Server runs without errors

**Initial Setup:**
- [ ] First login successful
- [ ] Dashboard displays correctly
- [ ] Added at least one colleague
- [ ] Added at least one output
- [ ] Created a task (v2.0)
- [ ] Set up Internal Panel member (v2.0)

**Testing v2.0 Features:**
- [ ] Tried colleague categories
- [ ] Marked someone as former staff
- [ ] Created an internal panel member
- [ ] Created and completed a task
- [ ] Tested CSV import
- [ ] Tested Excel export with links

**Production (Optional):**
- [ ] Background service configured
- [ ] Automatic startup enabled
- [ ] Backup script created
- [ ] Staff trained

---

**Version:** 2.0.0  
**Last Updated:** November 3, 2025  
**Quick Start Guide prepared by:** George Tsoulas

**Need more help?** See the complete documentation suite or contact your system administrator.

**Ready to become a REF Manager pro?** Read the User Guide next! 📖
