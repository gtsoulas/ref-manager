# ref_manager/templatetags/ref_permissions.py
"""
Template Tags for REF-Manager Access Control

These template tags allow checking permissions directly in templates.

Usage:
    {% load ref_permissions %}
    
    {# Check if user can edit an output #}
    {% if output|can_edit:user.ref_profile %}
        <a href="{% url 'output-edit' output.pk %}">Edit</a>
    {% endif %}
    
    {# Show role badges #}
    {% user_role_badges user.ref_profile %}
    
    {# Check specific permission #}
    {% if user.ref_profile|has_permission:'can_export_data' %}
        <a href="{% url 'export' %}">Export</a>
    {% endif %}
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# ==========================================
# Output permission filters
# ==========================================

@register.filter
def can_view(output, user_profile):
    """
    Check if user can view this output.
    
    Usage:
        {% if output|can_view:user.ref_profile %}
            {# show output #}
        {% endif %}
    """
    if not user_profile:
        return False
    
    # Can view all outputs?
    if user_profile.can_view_all_outputs:
        return True
    
    # Owner?
    if hasattr(output, 'owner') and output.owner == user_profile:
        return True
    
    # Linked colleague?
    if hasattr(output, 'colleague') and output.colleague:
        if hasattr(output.colleague, 'user_profile') and output.colleague.user_profile == user_profile:
            return True
    
    # Assigned panel member?
    if user_profile.is_panel_member:
        if hasattr(output, 'panel_assignments'):
            return output.panel_assignments.filter(panel_member=user_profile).exists()
    
    return False


@register.filter
def can_edit(output, user_profile):
    """
    Check if user can edit this output.
    
    Usage:
        {% if output|can_edit:user.ref_profile %}
            <a href="{% url 'output-edit' output.pk %}">Edit</a>
        {% endif %}
    """
    if not user_profile:
        return False
    
    # Can edit any output? (Admin)
    if user_profile.can_edit_any_output:
        return True
    
    # Cannot create = cannot edit
    if not user_profile.can_create_outputs:
        return False
    
    # Owner?
    if hasattr(output, 'owner') and output.owner == user_profile:
        return True
    
    # Linked colleague?
    if hasattr(output, 'colleague') and output.colleague:
        if hasattr(output.colleague, 'user_profile') and output.colleague.user_profile == user_profile:
            return True
    
    return False


@register.filter
def can_delete(output, user_profile):
    """
    Check if user can delete this output.
    
    Usage:
        {% if output|can_delete:user.ref_profile %}
            <a href="{% url 'output-delete' output.pk %}">Delete</a>
        {% endif %}
    """
    if not user_profile:
        return False
    return user_profile.can_delete_any_output


@register.filter
def is_owner(output, user_profile):
    """
    Check if user owns this output.
    
    Usage:
        {% if output|is_owner:user.ref_profile %}
            {# show owner-specific options #}
        {% endif %}
    """
    if not user_profile:
        return False
    
    if hasattr(output, 'owner') and output.owner == user_profile:
        return True
    
    if hasattr(output, 'colleague') and output.colleague:
        if hasattr(output.colleague, 'user_profile') and output.colleague.user_profile == user_profile:
            return True
    
    return False


# ==========================================
# Rating permission filters
# ==========================================

@register.filter
def can_rate(output, user_profile):
    """
    Check if user can rate this output.
    
    Usage:
        {% if output|can_rate:user.ref_profile %}
            <a href="{% url 'rating-create' output.pk %}">Add Rating</a>
        {% endif %}
    """
    if not user_profile:
        return False
    
    # Must have rating permission
    if not user_profile.can_rate_assigned:
        return False
    
    # Admin can rate anything
    if user_profile.is_admin:
        return True
    
    # Panel members can rate if assigned
    if user_profile.is_panel_member:
        if hasattr(output, 'panel_assignments'):
            return output.panel_assignments.filter(panel_member=user_profile).exists()
    
    return False


@register.filter
def can_edit_rating(rating, user_profile):
    """
    Check if user can edit this rating.
    
    Usage:
        {% if rating|can_edit_rating:user.ref_profile %}
            <a href="{% url 'rating-edit' rating.pk %}">Edit</a>
        {% endif %}
    """
    if not user_profile:
        return False
    return rating.can_edit(user_profile)


@register.filter
def can_finalise_rating(rating, user_profile):
    """
    Check if user can finalise this rating.
    
    Usage:
        {% if rating|can_finalise_rating:user.ref_profile %}
            <button>Finalise Rating</button>
        {% endif %}
    """
    if not user_profile:
        return False
    return rating.can_finalise(user_profile)


# ==========================================
# Role and permission filters
# ==========================================

@register.filter
def has_role(user_profile, role_code):
    """
    Check if user has a specific role.
    
    Usage:
        {% if user.ref_profile|has_role:'ADMIN' %}
            {# admin content #}
        {% endif %}
    """
    if not user_profile:
        return False
    return user_profile.has_role(role_code)


@register.filter
def has_permission(user_profile, permission_name):
    """
    Check if user has a specific permission (from any role).
    
    Usage:
        {% if user.ref_profile|has_permission:'can_export_data' %}
            <a href="{% url 'export' %}">Export</a>
        {% endif %}
    """
    if not user_profile:
        return False
    return getattr(user_profile, permission_name, False)


@register.filter
def is_assigned_to(output, user_profile):
    """
    Check if user is assigned to rate this output.
    
    Usage:
        {% if output|is_assigned_to:user.ref_profile %}
            {# show rating interface #}
        {% endif %}
    """
    if not user_profile:
        return False
    
    if not user_profile.is_panel_member:
        return False
    
    if hasattr(output, 'panel_assignments'):
        return output.panel_assignments.filter(panel_member=user_profile).exists()
    
    return False


# ==========================================
# Display tags
# ==========================================

@register.simple_tag
def user_role_badges(user_profile):
    """
    Return HTML badges for all user roles.
    Shows multiple badges if user has multiple roles.
    
    Usage:
        {% user_role_badges user.ref_profile %}
    """
    if not user_profile:
        return mark_safe('<span class="text-muted">Not logged in</span>')
    
    # Import here to avoid circular imports at module load
    from core.models_access_control import Role
    
    badge_styles = {
        Role.ADMIN: ('bg-danger', 'Admin'),
        Role.OBSERVER: ('bg-info', 'Observer'),
        Role.INTERNAL_PANEL: ('bg-warning text-dark', 'Panel'),
        Role.COLLEAGUE: ('bg-secondary', 'Colleague'),
    }
    
    badges = []
    for role in user_profile.roles.all():
        style, label = badge_styles.get(role.code, ('bg-light text-dark', role.name))
        badges.append(f'<span class="badge {style}">{label}</span>')
    
    if badges:
        return mark_safe(' '.join(badges))
    return mark_safe('<span class="text-muted">No roles</span>')


@register.simple_tag
def permission_icon(user_profile, permission_name):
    """
    Return an icon indicating if user has a permission.
    
    Usage:
        {% permission_icon user.ref_profile 'can_export_data' %}
    """
    if not user_profile:
        return mark_safe('<span class="text-muted">-</span>')
    
    has_perm = getattr(user_profile, permission_name, False)
    if has_perm:
        return mark_safe('<span class="text-success" title="Yes">✓</span>')
    return mark_safe('<span class="text-danger" title="No">✗</span>')


@register.simple_tag
def rating_status_badge(rating):
    """
    Return an HTML badge showing rating status.
    
    Usage:
        {% rating_status_badge rating %}
    """
    if not rating:
        return mark_safe('<span class="badge bg-secondary">No rating</span>')
    
    if rating.is_final:
        return mark_safe(
            f'<span class="badge bg-success">{rating.get_rating_display()} (Final)</span>'
        )
    
    if rating.rating == 0:
        return mark_safe('<span class="badge bg-warning text-dark">Not rated</span>')
    
    return mark_safe(
        f'<span class="badge bg-primary">{rating.get_rating_display()} (Draft)</span>'
    )


# ==========================================
# Inclusion tags
# ==========================================

@register.inclusion_tag('ref_manager/includes/role_summary.html', takes_context=True)
def role_summary(context, user_profile=None):
    """
    Render a summary of user's roles and key permissions.
    
    Usage:
        {% role_summary %}
        {% role_summary user.ref_profile %}
    
    Requires template: ref_manager/includes/role_summary.html
    """
    if user_profile is None:
        user = context.get('user')
        if user and hasattr(user, 'ref_profile'):
            user_profile = user.ref_profile
    
    return {
        'profile': user_profile,
        'roles': user_profile.roles.all() if user_profile else [],
        'can_view_all': user_profile.can_view_all_outputs if user_profile else False,
        'can_edit_any': user_profile.can_edit_any_output if user_profile else False,
        'can_create': user_profile.can_create_outputs if user_profile else False,
        'can_rate': user_profile.can_rate_assigned if user_profile else False,
        'can_manage': user_profile.can_manage_users if user_profile else False,
        'can_export': user_profile.can_export_data if user_profile else False,
    }


@register.inclusion_tag('ref_manager/includes/output_actions.html', takes_context=True)
def output_actions(context, output, user_profile=None):
    """
    Render action buttons for an output based on user permissions.
    
    Usage:
        {% output_actions output %}
        {% output_actions output user.ref_profile %}
    
    Requires template: ref_manager/includes/output_actions.html
    """
    if user_profile is None:
        user = context.get('user')
        if user and hasattr(user, 'ref_profile'):
            user_profile = user.ref_profile
    
    return {
        'output': output,
        'profile': user_profile,
        'can_view': can_view(output, user_profile),
        'can_edit': can_edit(output, user_profile),
        'can_delete': can_delete(output, user_profile),
        'can_rate': can_rate(output, user_profile),
        'is_owner': is_owner(output, user_profile),
    }
