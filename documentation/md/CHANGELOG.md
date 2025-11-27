# REF-Manager Changelog

## Version History

---

## [3.0.0] - November 2024

### Major Release - Complete Feature Overhaul

This release introduces comprehensive role-based access control, risk assessment framework, portfolio optimisation, and multi-dimensional quality ratings.

### Added

#### Role-Based Access Control
- Four user roles: Administrator, Observer, Internal Panel, Colleague
- Multi-role support with combined permissions
- 13+ granular permissions per role
- Rating finalisation system
- Django admin integration
- Template tags for permission-based rendering
- Management commands: `setup_roles`, `assign_roles`

#### Risk Assessment Framework
- Content risk scoring (0-1 scale)
- Timeline risk based on publication status
- Open Access compliance tracking
- Panel alignment assessment
- Venue prestige scoring
- Configurable risk weights
- Automatic composite risk calculation
- Risk dashboard with visualisations

#### Portfolio Optimisation
- REFSubmission model for scenario planning
- SubmissionOutput through model
- Portfolio quality score (GPA-style)
- Portfolio risk score
- Representativeness metrics
- Equality score (staff inclusion)
- Gender balance tracking
- ECR representation score
- Interdisciplinary output scoring
- Configurable optimisation weights

#### Multi-Dimensional Quality Ratings
- Separate Internal Panel rating field
- Separate Critical Friend (External) rating field
- Self-Assessment rating for authors
- Automatic average calculation
- Decimal average support
- Specialist/Non-Specialist reviewer classification

#### Task Management System
- Task model with full workflow
- Categories: Administrative, Review, Submission, Communication
- Priority levels: Low, Medium, High, Urgent
- Status tracking: Pending, In Progress, Completed, Cancelled
- Due date management
- Overdue alerts
- Task dashboard

#### Export Enhancements
- Excel export for assignments
- CSV export for assignments
- Submission portfolio export
- Risk analysis JSON export

#### User Management Interface
- Web-based user list
- Role editing interface
- Bulk role assignment
- Quick role toggle

### Changed
- Dashboard updated for decimal average ratings
- Colleague model: added employment status tracking
- Colleague categories expanded (6 categories)
- Output model: comprehensive risk fields added
- Output status options expanded
- Improved filtering throughout

### Technical
- 15 database migrations
- New management commands
- Expanded template tag library
- Additional view mixins and decorators

---

## [2.1.0] - November 2024

### Added
- Self-evaluation ratings for outputs
- Specialist/Non-Specialist reviewer classification
- Enhanced dashboard statistics
- Improved output comparison tools

### Changed
- Quality rating display improvements
- Better filter functionality
- Enhanced export options

### Fixed
- Colleague category filter issues
- Template rendering bugs
- Migration ordering

---

## [2.0.0] - November 2024

### Added
- Internal Panel member management
- Internal Panel assignment system
- Critical Friend assignment system
- Employment status tracking (Current/Former)
- Colleague category system
- Output status workflow
- BibTeX import functionality
- CSV import with duplicate detection
- Output comparison and merge tools

### Changed
- Expanded output status options
- Improved dashboard
- Enhanced colleague filtering

---

## [1.0.0] - October 2024

### Initial Release

- Colleague management
- Research output tracking
- Critical Friend management
- Request system
- Internal review workflow
- Dashboard with statistics
- Excel export
- LaTeX report generation
- User authentication
- Bootstrap 4 interface

---

## Upgrade Guide

### Upgrading to 3.0.0

**Prerequisites:**
- Python 3.10+
- Existing 2.x installation

**Steps:**

1. **Backup your database**
   ```bash
   # SQLite
   cp db.sqlite3 db.sqlite3.backup
   
   # PostgreSQL
   pg_dump -U refuser refmanager > backup.sql
   ```

2. **Update code**
   ```bash
   git pull origin main
   # or download and replace files
   ```

3. **Update dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Set up roles**
   ```bash
   python manage.py setup_roles --create-profiles --superusers-admin
   ```

6. **Verify**
   - Check all users have profiles
   - Verify role assignments
   - Test key functionality

### Breaking Changes in 3.0

- UserProfile model required for all users
- Role system replaces simple is_staff checks
- New quality rating fields (internal, external, self)
- Risk fields on Output model
- REFSubmission replaces informal submission tracking

### Data Migration Notes

- Existing users get profiles automatically with `--create-profiles`
- Superusers become Administrators with `--superusers-admin`
- Existing quality ratings preserved in `quality_rating` field
- New rating fields initially empty

---

## Version Numbering

REF-Manager follows Semantic Versioning:
- **Major** (X.0.0): Breaking changes, major features
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes, minor improvements

---

## Roadmap

### Planned for 3.1
- Enhanced reporting templates
- Batch risk assessment updates
- Improved portfolio comparison
- Email notifications

### Planned for 3.2
- REF submission export formats
- Integration with institutional systems
- Advanced analytics dashboard
- Audit logging

### Under Consideration
- API for external integrations
- Mobile-responsive improvements
- Multi-institution support
- REF 2029 specific templates
