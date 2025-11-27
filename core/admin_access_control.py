# ref_manager/admin_access_control.py
"""
Django Admin Configuration for REF-Manager Access Control

This module extends the Django admin to manage:
- Roles and permissions
- User profiles with multiple roles
- Panel assignments
- Internal ratings

Usage:
    # In your existing admin.py, add:
    from .admin_access_control import *
    
    # Or import specific admins:
    from .admin_access_control import (
        RoleAdmin, UserProfileAdmin, PanelAssignmentAdmin, InternalRatingAdmin
    )
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone

from .models_access_control import Role, UserProfile, PanelAssignment, InternalRating


# ==========================================
# Role Admin
# ==========================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin for Role model.
    Roles are usually pre-populated by migration and rarely edited.
    """
    list_display = (
        'code', 'name', 
        'can_view_all_outputs', 'can_edit_any_output',
        'can_create_outputs', 'can_rate_assigned', 'can_manage_users'
    )
    list_filter = (
        'can_view_all_outputs', 'can_edit_any_output', 
        'can_manage_users', 'can_rate_assigned'
    )
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description')
        }),
        ('View Permissions', {
            'fields': (
                'can_view_all_outputs', 
                'can_view_all_colleagues', 
                'can_view_all_ratings'
            ),
            'classes': ('collapse',)
        }),
        ('Edit Permissions', {
            'fields': (
                'can_edit_any_output', 
                'can_delete_any_output',
                'can_edit_any_rating', 
                'can_create_outputs'
            ),
            'classes': ('collapse',)
        }),
        ('Rating Permissions', {
            'fields': (
                'can_rate_assigned', 
                'can_unfinalise_ratings'
            ),
            'classes': ('collapse',)
        }),
        ('Admin Permissions', {
            'fields': (
                'can_manage_users', 
                'can_assign_panel', 
                'can_export_data', 
                'can_import_data'
            ),
            'classes': ('collapse',)
        }),
    )


# ==========================================
# User Profile Admin (Inline)
# ==========================================

class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile within User admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'REF Profile'
    filter_horizontal = ('roles',)  # Nice widget for many-to-many
    
    fieldsets = (
        ('Roles', {
            'fields': ('roles',),
            'description': 'Select one or more roles. Permissions are combined.'
        }),
        ('Linked Colleague', {
            'fields': ('linked_colleague',),
            'classes': ('collapse',)
        }),
    )


class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin with REF profile inline"""
    inlines = (UserProfileInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'is_staff', 'is_active', 'get_ref_roles'
    )
    list_filter = BaseUserAdmin.list_filter + ('ref_profile__roles',)
    
    def get_ref_roles(self, obj):
        """Display user's REF roles in list view"""
        if hasattr(obj, 'ref_profile'):
            roles = obj.ref_profile.roles.all()
            if roles:
                return ", ".join(r.name for r in roles)
        return '-'
    get_ref_roles.short_description = 'REF Roles'


# Re-register UserAdmin with our custom version
# Only do this if User is already registered
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)


# ==========================================
# User Profile Admin (Standalone)
# ==========================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Standalone UserProfile admin for bulk role management"""
    list_display = (
        'user', 'get_roles', 'linked_colleague', 
        'get_permissions_summary'
    )
    list_filter = ('roles',)
    search_fields = (
        'user__username', 'user__email', 
        'user__first_name', 'user__last_name',
        'linked_colleague__name'
    )
    raw_id_fields = ('linked_colleague',)
    filter_horizontal = ('roles',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Roles', {
            'fields': ('roles',),
            'description': 'Select one or more roles. Permissions are combined (most permissive wins).'
        }),
        ('Linked Colleague', {
            'fields': ('linked_colleague',),
            'description': 'Link to the Colleague record for this user.'
        }),
    )
    
    def get_roles(self, obj):
        """Display roles in list view"""
        return obj.get_role_display()
    get_roles.short_description = 'Roles'
    
    def get_permissions_summary(self, obj):
        """Show key permissions for quick reference"""
        perms = []
        if obj.can_view_all_outputs:
            perms.append('👁️ View All')
        if obj.can_edit_any_output:
            perms.append('✏️ Edit Any')
        if obj.can_create_outputs:
            perms.append('➕ Create')
        if obj.can_rate_assigned:
            perms.append('⭐ Rate')
        if obj.can_manage_users:
            perms.append('👥 Manage')
        if obj.can_export_data:
            perms.append('📤 Export')
        return ' | '.join(perms) or '⛔ No permissions'
    get_permissions_summary.short_description = 'Permissions'
    
    # Bulk actions for role management
    actions = [
        'add_admin_role', 'add_observer_role', 
        'add_panel_role', 'add_colleague_role', 
        'remove_all_roles'
    ]
    
    def add_admin_role(self, request, queryset):
        """Add Admin role to selected users"""
        role = Role.objects.get(code=Role.ADMIN)
        for profile in queryset:
            profile.roles.add(role)
        self.message_user(
            request, 
            f"Added Admin role to {queryset.count()} user(s)"
        )
    add_admin_role.short_description = "➕ Add Admin role"
    
    def add_observer_role(self, request, queryset):
        """Add Observer role to selected users"""
        role = Role.objects.get(code=Role.OBSERVER)
        for profile in queryset:
            profile.roles.add(role)
        self.message_user(
            request, 
            f"Added Observer role to {queryset.count()} user(s)"
        )
    add_observer_role.short_description = "➕ Add Observer role"
    
    def add_panel_role(self, request, queryset):
        """Add Internal Panel role to selected users"""
        role = Role.objects.get(code=Role.INTERNAL_PANEL)
        for profile in queryset:
            profile.roles.add(role)
        self.message_user(
            request, 
            f"Added Internal Panel role to {queryset.count()} user(s)"
        )
    add_panel_role.short_description = "➕ Add Internal Panel role"
    
    def add_colleague_role(self, request, queryset):
        """Add Colleague role to selected users"""
        role = Role.objects.get(code=Role.COLLEAGUE)
        for profile in queryset:
            profile.roles.add(role)
        self.message_user(
            request, 
            f"Added Colleague role to {queryset.count()} user(s)"
        )
    add_colleague_role.short_description = "➕ Add Colleague role"
    
    def remove_all_roles(self, request, queryset):
        """Remove all roles from selected users"""
        for profile in queryset:
            profile.roles.clear()
        self.message_user(
            request, 
            f"Removed all roles from {queryset.count()} user(s)"
        )
    remove_all_roles.short_description = "⛔ Remove all roles"


# ==========================================
# Panel Assignment Admin
# ==========================================

@admin.register(PanelAssignment)
class PanelAssignmentAdmin(admin.ModelAdmin):
    """Admin for assigning outputs to panel members"""
    list_display = (
        'output', 'panel_member', 'assigned_date', 
        'assigned_by', 'get_rating_status'
    )
    list_filter = ('assigned_date', 'panel_member__user')
    search_fields = (
        'output__title', 
        'panel_member__user__username',
        'panel_member__user__first_name',
        'panel_member__user__last_name'
    )
    raw_id_fields = ('output', 'panel_member')
    date_hierarchy = 'assigned_date'
    autocomplete_fields = ['output']
    readonly_fields = ('assigned_date', 'assigned_by')
    
    fieldsets = (
        (None, {
            'fields': ('output', 'panel_member')
        }),
        ('Assignment Info', {
            'fields': ('assigned_date', 'assigned_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_rating_status(self, obj):
        """Show if this assignment has been rated"""
        try:
            rating = InternalRating.objects.get(
                output=obj.output, 
                rater=obj.panel_member
            )
            if rating.is_final:
                return f"✅ {rating.get_rating_display()} (Final)"
            if rating.rating == 0:
                return "⏳ Started (Not rated)"
            return f"⏳ {rating.get_rating_display()} (Draft)"
        except InternalRating.DoesNotExist:
            return "❌ Not started"
    get_rating_status.short_description = 'Rating Status'
    
    def save_model(self, request, obj, form, change):
        """Set assigned_by when creating new assignment"""
        if not change:
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit panel_member choices to users with Internal Panel role"""
        if db_field.name == "panel_member":
            kwargs["queryset"] = UserProfile.objects.filter(
                roles__code=Role.INTERNAL_PANEL
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ==========================================
# Internal Rating Admin
# ==========================================

@admin.register(InternalRating)
class InternalRatingAdmin(admin.ModelAdmin):
    """Admin for viewing and managing internal ratings"""
    list_display = (
        'output', 'rater', 'rating', 'is_final', 
        'finalised_date', 'modified_date'
    )
    list_filter = ('is_final', 'rating', 'rater__user')
    search_fields = (
        'output__title', 
        'rater__user__username',
        'rater__user__first_name',
        'rater__user__last_name',
        'comments'
    )
    raw_id_fields = ('output', 'rater')
    readonly_fields = ('created_date', 'modified_date', 'finalised_date')
    date_hierarchy = 'created_date'
    
    fieldsets = (
        (None, {
            'fields': ('output', 'rater')
        }),
        ('Rating', {
            'fields': ('rating', 'comments')
        }),
        ('Status', {
            'fields': ('is_final', 'finalised_date'),
            'description': 'Finalised ratings cannot be changed except by admins.'
        }),
        ('Audit Trail', {
            'fields': ('created_date', 'modified_date'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['finalise_ratings', 'unfinalise_ratings']
    
    def finalise_ratings(self, request, queryset):
        """Finalise selected ratings"""
        # Only finalise ratings that have an actual rating
        valid = queryset.filter(is_final=False, rating__gt=0)
        count = valid.update(
            is_final=True, 
            finalised_date=timezone.now()
        )
        skipped = queryset.filter(rating=0).count()
        
        msg = f"✅ {count} rating(s) finalised"
        if skipped:
            msg += f" ({skipped} skipped - no rating)"
        self.message_user(request, msg)
    finalise_ratings.short_description = "✅ Finalise selected ratings"
    
    def unfinalise_ratings(self, request, queryset):
        """Un-finalise selected ratings (admin only)"""
        count = queryset.update(is_final=False, finalised_date=None)
        self.message_user(
            request, 
            f"🔓 {count} rating(s) un-finalised"
        )
    unfinalise_ratings.short_description = "🔓 Un-finalise selected ratings"
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit rater choices to users with rating permission"""
        if db_field.name == "rater":
            kwargs["queryset"] = UserProfile.objects.filter(
                roles__code__in=[Role.ADMIN, Role.INTERNAL_PANEL]
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
