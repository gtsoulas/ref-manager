# Changelog

**REF-Manager** - Research Excellence Framework Output Management System

**Author:** George Tsoulas  
**Institution:** University of York, Department of Language and Linguistic Science

All notable changes to REF-Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0] - 2025-12-03

### Added

#### O/S/R Rating System
- Three-component decimal ratings (0.00-4.00) for Originality, Significance, and Rigour
- Rating fields for three sources: Self-Assessment, Internal Panel, Critical Friend
- New model fields on Output:
  - `originality_self`, `significance_self`, `rigour_self`
  - `originality_internal`, `significance_internal`, `rigour_internal`
  - `originality_external`, `significance_external`, `rigour_external`
- Computed properties:
  - `osr_self_average`
  - `osr_internal_average`
  - `osr_external_average`
  - `osr_combined_average`
  - `osr_combined_average_no_self`

#### DOI Auto-Fetch
- OpenAlex API integration for automatic metadata population
- New endpoint: `/outputs/fetch-doi/`
- Auto-populates: title, authors, venue, year, volume, issue, pages, OA status, citation count, keywords
- JavaScript-powered form auto-fill with loading indicators

#### Enhanced Bulk Import
- New bulk import view at `/outputs/bulk-import/`
- Three import modes:
  - Hybrid (recommended): Fetches DOI metadata when available, uses CSV otherwise
  - Smart: Only imports rows with DOIs
  - Manual: Uses CSV data directly, no API calls
- Duplicate detection by DOI and exact title match
- Auto-link to colleagues via staff_id column
- Default OA status assignment option

#### OA Compliance Tracking
- New fields on Output model:
  - `acceptance_date`: Date paper was accepted
  - `deposit_date`: Date uploaded to repository
  - `embargo_end_date`: When full-text becomes available
  - `oa_status`: Choices (gold, green, hybrid, bronze, closed, non_compliant)
  - `oa_exception`: Exception type if non-compliant
  - `oa_compliance_notes`: Free-text notes
- Automatic compliance checking method `check_oa_compliance()`
- Visual compliance status display `get_compliance_status_display()`
- Bootstrap badge generator `get_oa_status_badge()`

#### REF Narrative Statements
- `double_weighting_statement`: TextField with 300 word limit, required if double-weighted
- `interdisciplinary_statement`: TextField with 500 word limit
- Real-time word counting in forms with validation
- Cross-field validation in `OutputForm.clean()`

#### Enhanced Forms & UI
- Complete redesign of output edit form with O/S/R rating cards
- Color-coded rating sources (blue=internal, yellow=external, green=self)
- Rating guide showing star equivalents
- DOI lookup card with Auto-Fill button
- OA Compliance section with date pickers
- REF Narrative section with word counters

### Changed

- Output edit form completely redesigned with card-based layout
- Removed legacy star-rating dropdown fields from OutputForm
- Updated `InternalPanelAssignmentForm` to remove `assigned_date` (auto_now_add field)
- Admin classes updated for model field consistency

### Fixed

- **admin.py**: Fixed field references that don't exist in models:
  - Removed `is_internal` from CriticalFriendAdmin
  - Changed `reviewed_date` to `created_at` in InternalReviewAdmin
  - Removed `is_active`, `is_final` from REFSubmissionAdmin
  - Removed `accepted_date` from AssignmentAdmin readonly_fields
  - Changed `completed_at` to `completed_date` in RequestAdmin

- **forms.py**: Removed `assigned_date` from InternalPanelAssignmentForm (auto_now_add conflict)

- **views.py**: Fixed related_name usage:
  - Changed `internalpanelassignment_set` to `panel_assignments`

### Deprecated

- Legacy star-rating fields (`quality_rating_internal`, `quality_rating_external`, `quality_rating_self`) retained for backwards compatibility but no longer displayed in forms

---

## [3.1] - 2025-11-15

### Added
- Initial O/S/R fields on InternalPanelAssignment and CriticalFriendAssignment models
- Risk assessment dashboard
- BibTeX import support
- Output comparison with fuzzy matching

### Changed
- Improved duplicate detection algorithm

---

## [3.0] - 2025-10-01

### Added
- Multi-user role system (Administrator, Observer, Internal Panel Member, Colleague)
- Internal panel workflow
- Critical friend assignments
- Role-based access control

### Changed
- Database schema redesign for multi-user support

---

## [2.0] - 2025-08-01

### Added
- CSV bulk import
- Output filtering and search
- Task management system
- Request tracking

---

## [1.0] - 2025-06-01

### Added
- Initial release
- Basic output management
- Colleague tracking
- Simple quality ratings

---

## Migration Notes

### Upgrading to 4.0 from 3.x

1. **Backup your database** before upgrading
2. Install new dependency: `pip install requests`
3. Run migrations:
   ```bash
   python manage.py makemigrations core --name upgrade_to_v4
   python manage.py migrate
   ```
4. Replace updated files:
   - `models.py`
   - `forms.py`
   - `admin.py`
   - `views.py`
   - `urls.py`
   - `templates/core/output_form.html`
   - `templates/core/enhanced_bulk_import.html`

5. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. Restart services:
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

### Data Migration

Existing outputs will have NULL values for new O/S/R fields. These can be populated:
- Manually through the edit form
- Via bulk import with updated CSV
- Through Django shell for batch updates

Legacy star ratings are preserved but no longer displayed in the UI.
