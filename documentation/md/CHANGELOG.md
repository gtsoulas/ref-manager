# Changelog

All notable changes to REF Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-11-03

### Added

#### Employment Status Tracking
- Added `employment_status` field to Colleague model (current/former)
- Added `employment_end_date` field to track when employment ended
- Filtering in forms to show only current employees in dropdowns
- Badge display for employment status in colleague lists
- "Mark as former" functionality with confirmation page
- Employment status statistics in dashboard
- Historical data preservation for former staff

#### Enhanced Colleague Categories
- Added `colleague_category` field with 9 distinct types:
  - Independent Researcher
  - **Non-Independent Researcher** (for post-docs) ⭐ KEY FEATURE
  - Post-Doctoral Researcher
  - Research Assistant
  - Academic Staff
  - Support Staff
  - Current Employee
  - Former Employee
  - Co-author (External)
- Category counts displayed on colleague list page
- Filtering by category in colleague views
- Category-specific badges and visual indicators
- Auto-categorization of external co-authors in CSV import

#### Internal Panel System ⭐ MAJOR FEATURE
- New `InternalPanelMember` model for internal reviewers
- New `InternalPanelAssignment` model for internal evaluations
- Four panel member roles: Chair, Member, Specialist, External Liaison
- Complete CRUD operations for panel members
- Assignment tracking with four status types (assigned, in_progress, completed, deferred)
- Rating recommendations aligned with REF quality ratings (4*, 3*, 2*, 1*)
- Dashboard widget showing internal panel statistics:
  - Total panel members
  - Active assignments
  - Completed reviews
  - Quality rating distribution
  - Workload distribution
- Separate from Critical Friends (external) system
- Internal panel views, forms, and templates
- Expertise area tracking for panel members
- Availability toggle for panel members

#### Task Management System ⭐ MAJOR FEATURE
- New `Task` model for general task tracking
- Seven task categories:
  - Administrative
  - Submission
  - Review
  - Meeting
  - Documentation
  - Deadline
  - Other
- Four priority levels: Low, Medium, High, Urgent
- Four status types: Pending, In Progress, Completed, Cancelled
- User assignment and creation tracking
- Due date and start date management
- Task dashboard widget showing:
  - Urgent tasks (due within 7 days)
  - Overdue tasks
  - Tasks by status
  - Tasks by priority
- Complete task list and detail views
- Task creation, editing, and completion functionality
- Filter and search capabilities
- Quick task completion from list view

#### CSV Import Functionality ⭐ MAJOR FEATURE
- Bulk import for research outputs
- Bulk import for colleague data
- Upload interface with file validation
- CSV template download
- Comprehensive data validation:
  - Required field checking
  - Date format validation
  - Quality rating validation
  - Email matching to colleagues
- Duplicate detection by title and DOI
- Automatic linking to existing colleagues
- Auto-categorization of external co-authors
- Import summary and error reporting
- Batch processing support

#### Excel Export with Clickable Links ⭐ MAJOR FEATURE
- Export review assignments to Excel
- Clickable hyperlinks to paper PDF files
- Color-coded formatting:
  - Light blue background for Internal Panel assignments
  - Light yellow background for Critical Friends assignments
- Professional Excel formatting:
  - Frozen header row
  - Bold headers
  - Adjusted column widths
  - Border styling
- Comprehensive filtering options:
  - By reviewer type (Internal Panel / Critical Friends)
  - By specific reviewer
  - By output author
  - By assignment status
- Complete assignment information:
  - Reviewer name and email
  - Output title and author
  - Quality rating
  - Review status
  - Due date and priority
  - Direct PDF links
  - Notes
- Automatic filename generation with timestamp
- CSV export alternative also available

#### Request Management Enhancements
- "Mark as completed" functionality with confirmation page
- Completion timestamp tracking
- "Delete request" functionality with warning confirmation
- Visual status indicators with badges
- Enhanced action buttons in list view:
  - View (blue)
  - Edit (yellow)
  - Complete (green) - hidden for already completed requests
  - Delete (red)
- Success messages after completion or deletion
- Conditional button display based on request status

#### Dashboard Improvements
- New Internal Panel Statistics widget showing:
  - Panel member count by role
  - Active assignments count
  - Completed reviews count
  - Average quality rating from internal reviews
  - Workload distribution
- New Task Overview widget showing:
  - Urgent tasks count
  - Overdue tasks count
  - Tasks by status breakdown
  - Tasks by priority breakdown
- Employment status distribution in Staff Summary
- Category breakdown in colleague statistics
- Enhanced Recent Activity section

### Changed

- Enhanced colleague model with new status and category fields
- Updated colleague list view with category filters and statistics
- Improved colleague detail view with employment status display
- Updated dashboard to show Internal Panel and Task statistics
- Enhanced colleague forms with category and status dropdowns
- Modified dropdown filtering to respect employment status (current only)
- Updated colleague queryset filtering in assignment forms
- Improved admin interface with new filters for status and category
- Updated URL patterns for new views and features
- Enhanced navigation menu with new sections

### Fixed

- **Category field naming issue**: Resolved inconsistency between hyphenated ("non-independent") and underscore ("non_independent") versions in database
- **Python 3.13 compatibility**: Fixed Decimal * float multiplication error in required_outputs calculation by converting Decimal to float
- **Template syntax errors**: Fixed unbalanced if/endif blocks in request templates
- **URL routing errors**: Fixed missing URL patterns for request_detail, request_complete, request_delete
- **Form field references**: Fixed incorrect field path references in assignment forms (e.g., colleague__user__last_name)
- **Static file issues**: Resolved Django admin panel styling problems with collectstatic
- **Dropdown filtering**: Fixed filtering to show only current employees in assignment forms

---

## [1.0.0] - 2025-10-21

### Added

#### Initial Release
- Complete REF submission management system
- Django 4.2+ based web application
- SQLite database (development) with PostgreSQL support (production)
- User authentication and authorization
- Multi-user access with permissions

#### Core Features
- **Output Management**:
  - Add, edit, view, delete research outputs
  - Multiple publication types (Article, Book, Chapter, etc.)
  - Quality rating system (4*, 3*, 2*, 1*, Unclassified)
  - PDF file upload for publications
  - DOI and URL linking
  - REF eligibility tracking
  - Unit of Assessment assignment
  - Keywords and abstracts
  - Submission notes

- **Colleague Management**:
  - Staff information tracking
  - FTE (Full-Time Equivalent) management
  - Unit of Assessment assignment
  - Required output calculation
  - Output count tracking
  - Contact information
  - Research interests

- **Critical Friends System**:
  - External reviewer management
  - Institution and expertise tracking
  - Assignment to outputs
  - Review status tracking
  - Due dates and priorities
  - Rating and feedback recording
  - Availability management
  - Completion tracking

- **Request Management**:
  - REF-related request tracking
  - Multiple request types
  - Priority levels
  - Status tracking (Pending, In Progress)
  - Due dates
  - Output linking
  - Assignment to colleagues
  - Request history

- **Dashboard**:
  - Submission statistics
  - Quality profile visualization
  - Staff summary
  - Review progress tracking
  - Recent activity feed
  - Quick access to common tasks

- **Report Generation**:
  - LaTeX template-based reports
  - Multiple report types:
    - Submission Overview
    - Quality Profile Analysis
    - Staff Progress Report
    - Review Status Report
    - Comprehensive Report (all combined)
  - Three output formats:
    - LaTeX source (.tex)
    - Article format
    - Report format
    - Beamer presentation
  - Professional formatting with charts
  - Executive summaries
  - Detailed analysis sections

#### Administrative Features
- Django admin panel integration
- User management
- Bulk operations
- Data filtering and search
- Advanced querying
- System configuration

#### Technical Features
- Responsive Bootstrap 4 interface
- AJAX-based interactions
- Form validation
- File upload handling
- PDF viewing
- DOI linking
- Search and filter functionality
- Pagination
- Crispy forms integration

---

## [Unreleased]

### Planned Features

#### High Priority
- Email notification system for:
  - Task reminders
  - Review due dates
  - Request updates
  - System announcements
- Advanced search across all entities
- Export to Word/DOCX format
- API endpoints for external integrations
- Mobile app or responsive mobile views
- Batch operations for outputs and assignments

#### Medium Priority
- Advanced analytics and visualizations
- Customizable dashboard widgets
- Team collaboration features
- Version control for outputs
- Comment system for discussions
- File attachment support for requests
- Integration with institutional repositories
- Impact case study tracking
- Environment statement management

#### Low Priority
- Machine learning for quality prediction
- Automated reviewer matching
- Citation tracking integration
- Grant linkage
- Conference presentation tracking
- Teaching exemption calculation
- Workload modeling

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| **2.0.0** | 2025-11-03 | Major update with Internal Panel, Tasks, CSV Import, Excel Export, Enhanced Categories |
| **1.0.0** | 2025-10-21 | Initial release with core REF management features |

---

## Upgrade Notes

### Upgrading from 1.0.0 to 2.0.0

**Database Migrations Required:** Yes

**Steps:**

1. **Backup database**:
   ```bash
   cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)
   ```

2. **Pull/download new code**:
   ```bash
   git pull origin main
   # or download and extract new version
   ```

3. **Update dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Restart server**:
   ```bash
   # If using systemd:
   sudo systemctl restart ref-manager
   
   # If using development server:
   # Press Ctrl+C and restart
   python manage.py runserver
   ```

**Data Migration Notes:**

- **Colleague Categories**: Existing colleagues will have `colleague_category` set to `None`. Update manually or via admin panel.
- **Employment Status**: Existing colleagues will default to "current". Update as needed.
- **No data loss**: All existing data preserved.
- **New tables created**: Task, InternalPanelMember, InternalPanelAssignment.
- **Backward compatible**: Old data works with new system.

**Configuration Changes:**

No changes to `.env` required, but you may want to add:
```env
# Task Settings (optional)
DEFAULT_TASK_PRIORITY=medium
TASK_OVERDUE_THRESHOLD_DAYS=7

# Excel Export Settings (optional)
MAX_EXPORT_ROWS=10000
```

**Testing After Upgrade:**

1. ✅ Log in successfully
2. ✅ View dashboard (new widgets should appear)
3. ✅ Create a colleague with category
4. ✅ Create a task
5. ✅ Create an internal panel member
6. ✅ Try CSV import
7. ✅ Try Excel export
8. ✅ Test existing features still work

---

## Breaking Changes

### Version 2.0.0

**None** - v2.0.0 is fully backward compatible with v1.0.0.

All existing functionality preserved. New features are additions only.

---

## Security Updates

### Version 2.0.0
- Updated Django to 4.2+ (latest security patches)
- Enhanced form validation
- Improved file upload security
- CSV upload validation and sanitization

### Version 1.0.0
- Initial security implementation
- Django built-in authentication
- CSRF protection
- SQL injection prevention
- XSS protection

---

## Performance Improvements

### Version 2.0.0
- Optimized database queries with select_related() and prefetch_related()
- Improved dashboard loading with query optimization
- Better pagination for large datasets
- Efficient Excel export with streaming
- CSV import batch processing

### Version 1.0.0
- Initial performance optimization
- Database indexing
- Query optimization
- Static file caching

---

## Documentation Updates

### Version 2.0.0
- Complete documentation rewrite for v2.0
- Updated README with new features
- Enhanced Quick Start Guide
- Comprehensive User Guide covering all v2.0 features
- Updated Technical Documentation
- Enhanced Troubleshooting Guide
- This Changelog

### Version 1.0.0
- Initial documentation suite
- Installation guide
- User manual
- Technical reference

---

## Acknowledgments

**Version 2.0.0 Contributors:**
- George Tsoulas - Feature design and testing
- Department of Language and Linguistic Science staff - User feedback
- Claude (Anthropic) - Development assistance

**Version 1.0.0 Contributors:**
- George Tsoulas - Initial concept and requirements
- Department staff - Testing and feedback

---

## Support

For questions about changes in specific versions:
- Email: [support-email]
- Documentation: Complete docs in project folder
- GitHub Issues: [if using GitHub]

---

**Note:** This changelog follows [Keep a Changelog](https://keepachangelog.com/) principles and [Semantic Versioning](https://semver.org/).

**Version Format:** MAJOR.MINOR.PATCH
- MAJOR: Incompatible API changes
- MINOR: New functionality (backward compatible)
- PATCH: Bug fixes (backward compatible)

---

**Last Updated:** November 3, 2025  
**Maintained by:** George Tsoulas  
**Project:** REF Manager  
**Institution:** Department of Language and Linguistic Science, University of York
