# REF Manager v2.0

A comprehensive Research Excellence Framework (REF) submission management system built with Django.

## 🎯 Features

### Core Features
- **Output Management**: Track research outputs (publications, performances, exhibitions)
- **Staff Management**: Manage academic staff with employment status tracking
- **Critical Friends System**: Assign and track external peer reviews
- **Internal Evaluation Panel**: Manage internal reviewers and assessments
- **Unit of Assessment (UoA) Organization**: Organize outputs by research units
- **Report Generation**: Generate LaTeX reports for submissions
- **Dashboard Analytics**: View submission statistics and progress
- **User Authentication**: Secure login system with role-based access

### Recent Additions (v2.0)
- ✨ **Employment Status Tracking**: Current vs Former staff categorization
- ✨ **Colleague Categories**: Independent, Non-Independent, Post-doc, Academic, etc.
- ✨ **Task Management**: General task tracking with priorities and deadlines
- ✨ **CSV Import**: Bulk import outputs and colleagues
- ✨ **Excel Export**: Export review assignments with clickable links
- ✨ **Internal Panel Dashboard**: Dedicated statistics for internal reviewers
- ✨ **Request Management**: Enhanced complete/delete functionality
- ✨ **Filtered Dropdowns**: Show only current employees in assignment forms

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: Bootstrap 4, Crispy Forms
- **Report Generation**: LaTeX (template-based)
- **Export**: openpyxl for Excel generation
- **Server**: Gunicorn + Systemd

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL (for production)
- pip and virtualenv
- LaTeX distribution (for report generation)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ref-manager.git
cd ref-manager
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DB_NAME=ref_manager_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

**⚠️ SECURITY**: Never commit your actual `.env` file! It contains secrets.

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser

```bash
python manage.py createsuperuser
```

### 7. Collect static files (production only)

```bash
python manage.py collectstatic
```

### 8. Run development server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## 🔧 Configuration

### Database Setup

For production with PostgreSQL:

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb ref_manager_db
sudo -u postgres createuser your_db_user
sudo -u postgres psql
ALTER USER your_db_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ref_manager_db TO your_db_user;
\q
```

### Production Deployment with Systemd

1. Create systemd service file `/etc/systemd/system/ref-manager.service`:

```ini
[Unit]
Description=REF Manager Gunicorn Application
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/path/to/ref-manager
Environment="PATH=/path/to/ref-manager/venv/bin"
ExecStart=/path/to/ref-manager/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 config.wsgi:application

[Install]
WantedBy=multi-user.target
```

2. Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ref-manager
sudo systemctl start ref-manager
```

## 📁 Project Structure

```
ref-manager/
├── config/              # Project configuration
│   ├── settings.py     # Django settings (uses .env)
│   ├── urls.py         # Main URL configuration
│   └── wsgi.py         # WSGI configuration
├── core/               # Core application
│   ├── models.py       # Database models (11 models)
│   │   ├── Colleague (with employment_status & category)
│   │   ├── Output
│   │   ├── CriticalFriend
│   │   ├── CriticalFriendAssignment
│   │   ├── InternalPanelMember (NEW in v2.0)
│   │   ├── InternalPanelAssignment (NEW in v2.0)
│   │   ├── InternalReview
│   │   ├── Request
│   │   ├── Task (NEW in v2.0)
│   │   └── ... other models
│   ├── views.py        # View functions
│   ├── forms.py        # Django forms
│   ├── admin.py        # Admin configuration
│   └── urls.py         # App URL patterns
├── reports/            # Reports application
│   ├── views.py        # Report views
│   ├── latex_generator.py  # LaTeX generation
│   └── urls.py         # Report URLs
├── templates/          # HTML templates
│   ├── base.html
│   ├── core/
│   │   ├── dashboard.html (updated with panel stats)
│   │   ├── colleague_list.html (updated with categories)
│   │   ├── task_*.html (NEW in v2.0)
│   │   └── ...
│   └── ...
├── static/             # Static files (CSS, JS, images)
├── media/              # User-uploaded files
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (NOT in git!)
├── .env.example       # Environment template (safe to commit)
└── .gitignore         # Git ignore rules
```

## 🔐 Security Notes

### Critical Security Practices

1. **Never commit `.env` files** - They contain secrets!
2. **Generate a strong `SECRET_KEY`** for production:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```
3. **Set `DEBUG=False` in production**
4. **Configure `ALLOWED_HOSTS` properly**
5. **Use HTTPS in production**
6. **Regularly update dependencies**:
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

### What's Safe to Commit
✅ `.env.example` - Template without real secrets  
✅ `.gitignore` - Protects sensitive files  
✅ `requirements.txt` - Dependencies list  
✅ All Python code files  
✅ Templates and static files  

### What to NEVER Commit
❌ `.env` - Contains SECRET_KEY and passwords  
❌ `db.sqlite3` - Your database  
❌ `*.pyc` - Compiled Python files  
❌ `__pycache__/` - Python cache  
❌ `media/` - User uploads (usually)  
❌ `staticfiles/` - Collected static files  

## 📊 Usage

### Admin Interface

Access the admin panel at `http://localhost:8000/admin/` with your superuser credentials.

### Main Features

1. **Dashboard**: View overview of submissions and statistics
   - Colleague counts by category
   - Output statistics
   - Quality profile
   - Internal Panel statistics (NEW!)
   
2. **Outputs**: Add and manage research outputs
   - Import from CSV
   - Assign to reviewers
   - Track quality ratings

3. **Staff/Colleagues**: Manage colleague records
   - Current vs Former status
   - Categories: Independent, Non-Independent, Post-doc, etc.
   - Filter by employment status and category

4. **Critical Friends**: Assign external reviewers
   - Export assignments to Excel
   - Track review progress

5. **Internal Panel**: Manage internal reviewers (NEW!)
   - Assign panel members to outputs
   - Track internal assessments
   - View panel statistics on dashboard

6. **Tasks**: General task management (NEW!)
   - Create, assign, and track tasks
   - Priorities and deadlines
   - Categories and status tracking

7. **Reports**: Generate submission reports
   - LaTeX template-based generation
   - Multiple report types

## 🆕 New Features in v2.0

### Employment Status Tracking
- Mark colleagues as "Current" or "Former"
- Preserve historical data for former staff
- Filter dropdowns to show only current staff
- Track employment end dates

### Colleague Categories
- **Independent Researcher** - Established researchers
- **Non-Independent Researcher** - Post-docs, early career
- **Post-Doctoral Researcher** - Specific post-doc category
- **Research Assistant** - Research support staff
- **Academic Staff** - Teaching & research faculty
- **Support Staff** - Administrative support
- **Current Employee** - Generic current staff
- **Former Employee** - Past employees
- **Co-author (External)** - External collaborators

### Internal Panel System
- Separate from Critical Friends (external reviewers)
- Assign internal reviewers to outputs
- Track internal assessments
- Dashboard statistics
- Role management (Chair, Member, Specialist, etc.)

### Task Management
- Create and assign tasks
- Categories: Administrative, Submission, Review, etc.
- Priority levels: Low, Medium, High, Urgent
- Status tracking: Pending, In Progress, Completed, Cancelled
- Due dates and assignments

### CSV Import
- Bulk import research outputs
- Import colleague data
- Duplicate detection
- Automatic categorization

### Excel Export
- Export review assignments
- Clickable links to papers
- Color-coded by reviewer type
- Filter by status, reviewer, author

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write descriptive commit messages
- Update documentation for new features
- Test thoroughly before submitting PR
- Never commit sensitive data

## 📝 Version History

### v2.0 (Current)
- Added employment status tracking
- Added colleague categories (including non-independent)
- Added Internal Panel system
- Added Task management
- Added CSV import functionality
- Added Excel export with links
- Enhanced dashboard with panel statistics
- Improved filtering (current staff only in dropdowns)

### v1.0 (Initial Release)
- Core output management
- Staff/colleague tracking
- Critical Friends system
- Request management
- Basic reporting
- Dashboard analytics

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Built for managing REF submissions
- Designed for UK academic institutions
- Supports REF 2029 submission requirements

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Contact: your.email@example.com

## 🗺️ Roadmap

### Planned Features
- [ ] Email notifications for deadlines
- [ ] REST API for integrations
- [ ] Advanced analytics dashboard
- [ ] Mobile-responsive improvements
- [ ] Automated quality predictions
- [ ] Integration with institutional repositories

### Under Consideration
- [ ] Multi-institution support
- [ ] Collaborative editing
- [ ] Version control for outputs
- [ ] Impact case study tracking

---

**Note**: This is an academic submission management system. Ensure compliance with your institution's data protection policies (GDPR, data privacy) when handling staff and research data.

## 🔗 Useful Links

- [Django Documentation](https://docs.djangoproject.com/)
- [REF 2029 Guidelines](https://www.ref.ac.uk/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [LaTeX Documentation](https://www.latex-project.org/help/documentation/)

---

**Last Updated**: November 2025  
**Version**: 2.0  
**Status**: Production Ready
