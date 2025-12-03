# Changelog

## REF-Manager Version History

**Author**: George Tsoulas  
**Institution**: University of York, Department of Language and Linguistic Science

---

## [4.0.0] - 2025-12-03

### "REF 2029 Ready" Release

#### Added

**O/S/R Rating System**
- Three-component decimal ratings (0.00-4.00) for Originality, Significance, Rigour
- Ratings from three sources: Self-Assessment, Internal Panel, Critical Friend
- New model fields: `originality_self`, `significance_self`, `rigour_self`, `originality_internal`, `significance_internal`, `rigour_internal`, `originality_external`, `significance_external`, `rigour_external`
- Computed properties: `osr_self_average`, `osr_internal_average`, `osr_external_average`, `osr_combined_average`, `osr_combined_average_no_self`

**DOI Auto-Fetch**
- OpenAlex API integration for automatic metadata population
- Endpoint: `/outputs/fetch-doi/`
- Auto-populates: title, authors, venue, year, volume, issue, pages, OA status, citation count

**Enhanced Bulk Import**
- Three import modes: Hybrid, Smart, Manual
- Duplicate detection by DOI and title
- Auto-link to colleagues via staff_id
- URL: `/outputs/bulk-import/`

**Open Access Compliance**
- New fields: `acceptance_date`, `deposit_date`, `embargo_end_date`
- OA status tracking: Gold, Green, Hybrid, Bronze, Closed
- Automatic 3-month deposit rule compliance checking
- Exception recording for non-compliant outputs

**REF Narrative Statements**
- `double_weighting_statement` field (300 word limit)
- `interdisciplinary_statement` field (500 word limit)
- Real-time word counting with validation

**UI Enhancements**
- O/S/R rating cards (colour-coded by source)
- DOI lookup card with Auto-Fill button
- OA Compliance section with date pickers
- Rating guide showing star equivalents

#### Changed

- Output edit form redesigned with card-based layout
- Removed legacy star-rating dropdown fields from forms
- Updated admin configuration for model consistency

#### Fixed

- admin.py: Fixed references to non-existent fields (`is_internal`, `reviewed_date`, `is_active`, `is_final`)
- forms.py: Removed `assigned_date` from InternalPanelAssignmentForm (auto_now_add conflict)
- views.py: Fixed `internalpanelassignment_set` to `panel_assignments` (correct related_name)
- views.py: Fixed OpenAlex API URL format (`doi:` prefix instead of full URL)

---

## [3.1.0] - 2025-11-15

### Added
- Initial O/S/R fields on assignment models
- Risk assessment dashboard
- BibTeX import support
- Output comparison with fuzzy matching

### Changed
- Improved duplicate detection algorithm

---

## [3.0.0] - 2025-10-01

### Added
- Multi-user role system (Administrator, Observer, Internal Panel, Colleague)
- Internal panel workflow
- Critical friend assignments
- Role-based access control

### Changed
- Database schema redesign for multi-user support

---

## [2.0.0] - 2025-08-01

### Added
- CSV bulk import
- Output filtering and search
- Task management system
- Request tracking

---

## [1.0.0] - 2025-06-01

### Initial Release
- Basic output management
- Colleague tracking
- Simple quality ratings

---

## Upgrade Notes

### Upgrading to 4.0 from 3.x

1. **Backup your database** before upgrading

2. **Install new dependency:**
   ```bash
   pip install requests
   ```

3. **Run migrations:**
   ```bash
   python manage.py makemigrations core --name upgrade_to_v4
   python manage.py migrate
   ```

4. **Replace updated files:**
   - `models.py`, `forms.py`, `admin.py`, `views.py`, `urls.py`
   - `templates/core/output_form.html`
   - `templates/core/enhanced_bulk_import.html`

5. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Restart services:**
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

### Data Migration

Existing outputs will have NULL values for new O/S/R fields. These can be populated:
- Manually through the edit form
- Via bulk import with updated CSV
- Through Django shell for batch updates

Legacy star ratings are preserved in the database but no longer displayed.
