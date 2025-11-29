# O/S/R Three-Component Ratings Update

## Overview

This update adds comprehensive display of the three-component decimal ratings (Originality, Significance, Rigour) on a 0.00-4.00 scale to:

1. **Output Detail Page** - Shows individual O/S/R ratings for both Internal Panel and Critical Friends, plus a summary card with component averages
2. **Output List Page** - Shows decimal averages from all reviewers instead of the old star ratings

## Files Modified

- `core/models.py` - Added new methods for calculating decimal averages
- `templates/core/output_detail.html` - Added O/S/R display for Critical Friends + Summary card
- `templates/core/output_list.html` - Updated to show decimal averages

## Installation Instructions

### Step 1: Backup Current Files

```bash
cd /path/to/ref-manager
cp core/models.py core/models.py.backup
cp templates/core/output_detail.html templates/core/output_detail.html.backup
cp templates/core/output_list.html templates/core/output_list.html.backup
```

### Step 2: Copy New Files

```bash
# Extract the archive
tar -xzvf osr-ratings-update.tar.gz

# Copy files to their destinations
cp osr-ratings-update/models.py core/models.py
cp osr-ratings-update/output_detail.html templates/core/output_detail.html
cp osr-ratings-update/output_list.html templates/core/output_list.html
```

### Step 3: Verify (Development)

```bash
python manage.py check
python manage.py runserver
```

Visit an output detail page and the output list to verify the changes.

### Step 4: Deploy to Production

```bash
# If using Docker
docker-compose restart

# If using Gunicorn
sudo systemctl restart gunicorn
```

## New Model Methods

The following methods have been added to the `Output` model:

| Method | Description |
|--------|-------------|
| `get_internal_panel_osr_average()` | Returns decimal average of O/S/R across all Internal Panel assignments |
| `get_critical_friend_osr_average()` | Returns decimal average of O/S/R across all Critical Friend assignments |
| `get_combined_osr_average(include_self=False)` | Returns combined decimal average |
| `get_combined_osr_average_with_self()` | Wrapper for templates - includes self-assessment |
| `get_osr_breakdown()` | Returns dict with individual O, S, R averages and counts |

## Display Features

### Output Detail Page

- **Critical Friends section**: Now shows O/S/R ratings for each assignment
- **New "O/S/R Ratings Summary" card**: Shows:
  - Individual component averages (Originality, Significance, Rigour)
  - Number of ratings for each component
  - Overall average
  - Combined averages (with/without self-assessment)

### Output List Page

- Shows decimal averages from Internal Panel and Critical Friends
- Combined average displayed on 0-4 scale
- Color-coded based on rating level:
  - Green (≥3.5): Excellent
  - Blue (≥2.5): Good
  - Yellow (≥1.5): Moderate
  - Grey (<1.5): Needs improvement

## Rating Entry

Ratings are entered through the existing Internal Panel Assignment and Critical Friend Assignment forms. Each form should include fields for:

- Originality (0.00-4.00)
- Significance (0.00-4.00)
- Rigour (0.00-4.00)

The `component_average_rating` is calculated automatically when saving.

## Troubleshooting

### Ratings Not Showing

1. Check that ratings have been entered in the assignment forms
2. Verify the database has the O/S/R fields populated:

```python
python manage.py shell
from core.models import InternalPanelAssignment
for a in InternalPanelAssignment.objects.all()[:5]:
    print(f"ID:{a.id} O:{a.originality_rating} S:{a.significance_rating} R:{a.rigour_rating}")
```

### Template Errors

If you see template errors, ensure Django can access the new model methods:

```python
python manage.py shell
from core.models import Output
o = Output.objects.first()
print(o.get_osr_breakdown())
print(o.get_combined_osr_average())
```

## Rollback

To rollback to previous version:

```bash
cp core/models.py.backup core/models.py
cp templates/core/output_detail.html.backup templates/core/output_detail.html
cp templates/core/output_list.html.backup templates/core/output_list.html
```
