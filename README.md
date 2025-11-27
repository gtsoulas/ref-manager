# REF-Manager Access Control System

A comprehensive Role-Based Access Control (RBAC) system for REF-Manager with multi-role support.

## Features

- **Four distinct roles**: Admin, Observer, Internal Panel, Colleague
- **Multi-role support**: Users can have multiple roles; permissions are combined
- **Granular permissions**: 13+ individual permissions per role
- **Rating finalisation**: Lock ratings to prevent changes
- **Full Django integration**: Mixins, decorators, template tags, admin interface

## Quick Start

### Installation

```bash
# Navigate to your REF-Manager project
cd ~/REF-Stuff/ref-manager

# Copy the package files (adjust path as needed)
cp -r /path/to/access_control_package/* .

# Run the installation script
chmod +x install_access_control.sh
./install_access_control.sh
```

### Manual Installation

If you prefer to install manually:

1. Copy files to your `ref_manager` app:
   - `models_access_control.py`
   - `mixins.py`
   - `decorators.py`
   - `admin_access_control.py`
   - `templatetags/ref_permissions.py`
   - `management/commands/assign_roles.py`
   - `management/commands/setup_roles.py`

2. Update `models.py`:
   ```python
   from .models_access_control import Role, UserProfile, PanelAssignment, InternalRating
   ```

3. Update `admin.py`:
   ```python
   from .admin_access_control import *
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations ref_manager
   python manage.py migrate
   python manage.py setup_roles --create-profiles --superusers-admin
   ```

## Roles

| Role | Code | Description |
|------|------|-------------|
| **Administrator** | `ADMIN` | Full access to everything |
| **Observer** | `OBSERVER` | Read-only access to everything |
| **Internal Panel** | `INTERNAL_PANEL` | Own outputs + rate assigned outputs |
| **Colleague** | `COLLEAGUE` | Own outputs only |

### Multi-Role Examples

| Combination | Use Case |
|-------------|----------|
| Observer + Colleague | Senior staff who need oversight but also submit research |
| Observer + Internal Panel | External reviewer who rates specific outputs |

## Usage

### In Views (Class-Based)

```python
from ref_manager.mixins import (
    AdminRequiredMixin, 
    OutputAccessMixin,
    CanEditMixin
)

class OutputListView(OutputAccessMixin, ListView):
    """Automatically filters outputs based on user permissions"""
    model = Output
    template_name = 'outputs/list.html'

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Only accessible by admins"""
    template_name = 'admin/dashboard.html'
```

### In Views (Function-Based)

```python
from ref_manager.decorators import (
    admin_required,
    permission_required,
    output_edit_permission
)

@admin_required
def admin_only_view(request):
    ...

@permission_required('can_export_data')
def export_view(request):
    ...

@output_edit_permission
def edit_output(request, pk):
    # request.output is automatically set
    output = request.output
    ...
```

### In Templates

```html
{% load ref_permissions %}

{# Check permissions #}
{% if output|can_edit:user.ref_profile %}
    <a href="{% url 'output-edit' output.pk %}">Edit</a>
{% endif %}

{# Show role badges #}
{% user_role_badges user.ref_profile %}

{# Role summary card #}
{% role_summary %}

{# Check specific permission #}
{% if user.ref_profile|has_permission:'can_export_data' %}
    <a href="{% url 'export' %}">Export Data</a>
{% endif %}
```

### Command Line

```bash
# List all users and their roles
python manage.py assign_roles --list

# Show detailed info for a user
python manage.py assign_roles jane.smith --show

# Add a role
python manage.py assign_roles jane.smith --add OBSERVER

# Add multiple roles
python manage.py assign_roles john.doe --add OBSERVER INTERNAL_PANEL

# Set exact roles (removes others)
python manage.py assign_roles admin --set ADMIN

# Remove a role
python manage.py assign_roles jane.smith --remove INTERNAL_PANEL

# Clear all roles
python manage.py assign_roles jane.smith --clear
```

## Permission Matrix

### Output Permissions

| Action | Admin | Observer | Panel | Colleague |
|--------|:-----:|:--------:|:-----:|:---------:|
| View all | ✅ | ✅ | ❌ | ❌ |
| View own | ✅ | ✅ | ✅ | ✅ |
| View assigned | ✅ | ✅ | ✅ | ❌ |
| Create own | ✅ | ❌ | ✅ | ✅ |
| Edit own | ✅ | ❌ | ✅ | ✅ |
| Edit any | ✅ | ❌ | ❌ | ❌ |
| Delete any | ✅ | ❌ | ❌ | ❌ |

### Rating Permissions

| Action | Admin | Observer | Panel | Colleague |
|--------|:-----:|:--------:|:-----:|:---------:|
| View all | ✅ | ✅ | ❌ | ❌ |
| Rate assigned | ✅ | ❌ | ✅ | ❌ |
| Edit own rating | ✅ | ❌ | ✅* | ❌ |
| Finalise rating | ✅ | ❌ | ✅ | ❌ |
| Un-finalise | ✅ | ❌ | ❌ | ❌ |

*Only if not finalised

## API Reference

### UserProfile Properties

```python
profile = request.user.ref_profile

# Role checks
profile.is_admin           # True if has Admin role
profile.is_observer        # True if has Observer role
profile.is_panel_member    # True if has Internal Panel role
profile.is_colleague       # True if has Colleague role

# Permission checks (combined from all roles)
profile.can_view_all_outputs
profile.can_view_all_colleagues
profile.can_view_all_ratings
profile.can_edit_any_output
profile.can_delete_any_output
profile.can_edit_any_rating
profile.can_create_outputs
profile.can_rate_assigned
profile.can_unfinalise_ratings
profile.can_manage_users
profile.can_assign_panel
profile.can_export_data
profile.can_import_data

# Role management
profile.has_role('ADMIN')
profile.has_any_role('ADMIN', 'OBSERVER')
profile.add_role('OBSERVER')
profile.remove_role('INTERNAL_PANEL')
profile.set_roles('ADMIN', 'COLLEAGUE')
profile.clear_roles()
```

### InternalRating Methods

```python
rating = InternalRating.objects.get(pk=1)

rating.finalise()           # Lock the rating
rating.unfinalise()         # Unlock (admin only)
rating.can_edit(profile)    # Check if user can edit
rating.can_finalise(profile) # Check if user can finalise
```

## File Structure

```
ref_manager/
├── models_access_control.py    # Role, UserProfile, PanelAssignment, InternalRating
├── mixins.py                   # Class-based view mixins
├── decorators.py               # Function-based view decorators
├── admin_access_control.py     # Django admin configuration
├── templatetags/
│   └── ref_permissions.py      # Template tags and filters
├── management/
│   └── commands/
│       ├── assign_roles.py     # Role management command
│       └── setup_roles.py      # Initial setup command
└── templates/
    └── ref_manager/
        └── includes/
            ├── role_summary.html    # Role display widget
            └── output_actions.html  # Action buttons widget
```

## Updating Your Existing Code

### 1. Add owner field to Output model

```python
# In models.py, add to your Output model:
owner = models.ForeignKey(
    'UserProfile',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='owned_outputs',
    help_text='User who created/owns this output'
)
```

### 2. Update your views

```python
# Before
class OutputListView(LoginRequiredMixin, ListView):
    model = Output

# After
from ref_manager.mixins import OutputAccessMixin

class OutputListView(OutputAccessMixin, ListView):
    model = Output
    # Queryset is automatically filtered!
```

### 3. Update your templates

```html
<!-- Before -->
{% if user.is_authenticated %}
    <a href="{% url 'output-edit' output.pk %}">Edit</a>
{% endif %}

<!-- After -->
{% load ref_permissions %}
{% if output|can_edit:user.ref_profile %}
    <a href="{% url 'output-edit' output.pk %}">Edit</a>
{% endif %}
```

## Troubleshooting

### "Role 'X' does not exist"

Run the setup command to create default roles:
```bash
python manage.py setup_roles
```

### "User has no profile"

Create profiles for existing users:
```bash
python manage.py setup_roles --create-profiles
```

### Circular import errors

Make sure you import using string references in ForeignKey fields:
```python
output = models.ForeignKey('Output', ...)  # String reference
```

## License

This access control system is part of REF-Manager, released under GPL v3.
