# ref_manager/models_access_control.py
"""
Access Control Models for REF-Manager

This module adds Role-Based Access Control (RBAC) with multi-role support.
Users can have multiple roles; permissions are combined (UNION - most permissive wins).

Roles:
- ADMIN: Full access to everything
- OBSERVER: Read-only access to everything  
- INTERNAL_PANEL: Own outputs + rate assigned outputs
- COLLEAGUE: Own outputs only

Usage:
    from core.models_access_control import Role, UserProfile, PanelAssignment, InternalRating
    
    # Check permissions
    if request.user.ref_profile.can_view_all_outputs:
        # Show all outputs
    
    # Check specific role
    if request.user.ref_profile.is_panel_member:
        # Show rating interface
    
    # Add role to user
    request.user.ref_profile.add_role(Role.OBSERVER)
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Role(models.Model):
    """
    REF-specific roles that define permissions.
    Users can have multiple roles - permissions are combined (union).
    
    The four default roles are created by data migration.
    Permissions are stored as boolean fields for flexibility.
    """
    
    # Role codes (used in code for permission checks)
    ADMIN = 'ADMIN'
    OBSERVER = 'OBSERVER'
    INTERNAL_PANEL = 'INTERNAL_PANEL'
    COLLEAGUE = 'COLLEAGUE'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (OBSERVER, 'Observer (Read-Only)'),
        (INTERNAL_PANEL, 'Internal Panel Member'),
        (COLLEAGUE, 'Colleague'),
    ]
    
    code = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        unique=True,
        primary_key=True
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    # ==========================================
    # Permission flags for this role
    # ==========================================
    
    # View permissions
    can_view_all_outputs = models.BooleanField(
        default=False,
        help_text="Can view all outputs in the system"
    )
    can_view_all_colleagues = models.BooleanField(
        default=False,
        help_text="Can view all colleague records"
    )
    can_view_all_ratings = models.BooleanField(
        default=False,
        help_text="Can view all internal ratings"
    )
    
    # Edit permissions
    can_edit_any_output = models.BooleanField(
        default=False,
        help_text="Can edit any output regardless of ownership"
    )
    can_delete_any_output = models.BooleanField(
        default=False,
        help_text="Can delete any output"
    )
    can_edit_any_rating = models.BooleanField(
        default=False,
        help_text="Can edit any rating including finalised ones"
    )
    
    # Create permissions
    can_create_outputs = models.BooleanField(
        default=False,
        help_text="Can create new outputs"
    )
    
    # Rating permissions
    can_rate_assigned = models.BooleanField(
        default=False,
        help_text="Can rate outputs assigned to this user"
    )
    can_unfinalise_ratings = models.BooleanField(
        default=False,
        help_text="Can un-finalise ratings that have been locked"
    )
    
    # Admin permissions
    can_manage_users = models.BooleanField(
        default=False,
        help_text="Can manage user accounts and roles"
    )
    can_assign_panel = models.BooleanField(
        default=False,
        help_text="Can assign outputs to panel members"
    )
    can_export_data = models.BooleanField(
        default=False,
        help_text="Can export data from the system"
    )
    can_import_data = models.BooleanField(
        default=False,
        help_text="Can import data into the system"
    )
    
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['code']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_default_permissions(cls):
        """Return default permission settings for each role"""
        return {
            cls.ADMIN: {
                'name': 'Administrator',
                'description': 'Full access to all features. REF coordinators and department administrators.',
                'can_view_all_outputs': True,
                'can_view_all_colleagues': True,
                'can_view_all_ratings': True,
                'can_edit_any_output': True,
                'can_delete_any_output': True,
                'can_edit_any_rating': True,
                'can_manage_users': True,
                'can_assign_panel': True,
                'can_export_data': True,
                'can_import_data': True,
                'can_create_outputs': True,
                'can_rate_assigned': True,
                'can_unfinalise_ratings': True,
            },
            cls.OBSERVER: {
                'name': 'Observer (Read-Only)',
                'description': 'Read-only access to all data. Critical friends, external reviewers, auditors.',
                'can_view_all_outputs': True,
                'can_view_all_colleagues': True,
                'can_view_all_ratings': True,
                'can_export_data': True,
            },
            cls.INTERNAL_PANEL: {
                'name': 'Internal Panel Member',
                'description': 'Can view and rate assigned outputs. Department panel members.',
                'can_create_outputs': True,
                'can_rate_assigned': True,
            },
            cls.COLLEAGUE: {
                'name': 'Colleague',
                'description': 'Can manage own outputs only. Regular staff members.',
                'can_create_outputs': True,
            },
        }


class UserProfile(models.Model):
    """
    Extended user profile with REF-specific roles.
    Users can have MULTIPLE roles - permissions are the UNION of all roles.
    
    Example combinations:
    - Observer + Colleague: Can see everything AND manage own outputs
    - Observer + Internal Panel: Can see everything AND rate assigned outputs
    - Admin + anything: Full access (Admin encompasses all permissions)
    """
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='ref_profile'
    )
    
    # Multiple roles via many-to-many
    roles = models.ManyToManyField(
        Role,
        related_name='users',
        blank=True,
        help_text="User can have multiple roles. Permissions are combined."
    )
    
    # Link to Colleague record (for output ownership)
    linked_colleague = models.OneToOneField(
        'Colleague',  # String reference to avoid circular import
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_profile',
        help_text="Link to Colleague record for this user"
    )
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        role_list = ", ".join(r.name for r in self.roles.all())
        return f"{self.user.username} ({role_list or 'No roles'})"
    
    # ==========================================
    # Role checking properties
    # ==========================================
    
    @property
    def role_codes(self):
        """Get set of role codes for efficient checking"""
        return set(self.roles.values_list('code', flat=True))
    
    @property
    def is_admin(self):
        """Check if user has Admin role"""
        return Role.ADMIN in self.role_codes
    
    @property
    def is_observer(self):
        """Check if user has Observer role"""
        return Role.OBSERVER in self.role_codes
    
    @property
    def is_panel_member(self):
        """Check if user has Internal Panel role"""
        return Role.INTERNAL_PANEL in self.role_codes
    
    @property
    def is_colleague(self):
        """Check if user has Colleague role"""
        return Role.COLLEAGUE in self.role_codes
    
    def has_role(self, role_code):
        """Check if user has a specific role"""
        return role_code in self.role_codes
    
    def has_any_role(self, *role_codes):
        """Check if user has any of the specified roles"""
        return bool(self.role_codes.intersection(role_codes))
    
    def has_all_roles(self, *role_codes):
        """Check if user has all of the specified roles"""
        return set(role_codes).issubset(self.role_codes)
    
    # ==========================================
    # Combined permission properties
    # Permissions are UNION of all roles (most permissive wins)
    # ==========================================
    
    def _has_permission(self, permission_name):
        """Check if any of the user's roles grant this permission"""
        return self.roles.filter(**{permission_name: True}).exists()
    
    @property
    def can_view_all_outputs(self):
        """Can view all outputs in the system"""
        return self._has_permission('can_view_all_outputs')
    
    @property
    def can_view_all_colleagues(self):
        """Can view all colleague records"""
        return self._has_permission('can_view_all_colleagues')
    
    @property
    def can_view_all_ratings(self):
        """Can view all internal ratings"""
        return self._has_permission('can_view_all_ratings')
    
    @property
    def can_edit_any_output(self):
        """Can edit any output regardless of ownership"""
        return self._has_permission('can_edit_any_output')
    
    @property
    def can_delete_any_output(self):
        """Can delete any output"""
        return self._has_permission('can_delete_any_output')
    
    @property
    def can_edit_any_rating(self):
        """Can edit any rating including finalised ones"""
        return self._has_permission('can_edit_any_rating')
    
    @property
    def can_manage_users(self):
        """Can manage user accounts and roles"""
        return self._has_permission('can_manage_users')
    
    @property
    def can_assign_panel(self):
        """Can assign outputs to panel members"""
        return self._has_permission('can_assign_panel')
    
    @property
    def can_export_data(self):
        """Can export data from the system"""
        return self._has_permission('can_export_data')
    
    @property
    def can_import_data(self):
        """Can import data into the system"""
        return self._has_permission('can_import_data')
    
    @property
    def can_create_outputs(self):
        """Can create new outputs"""
        return self._has_permission('can_create_outputs')
    
    @property
    def can_rate_assigned(self):
        """Can rate outputs assigned to this user"""
        return self._has_permission('can_rate_assigned')
    
    @property
    def can_unfinalise_ratings(self):
        """Can un-finalise ratings that have been locked"""
        return self._has_permission('can_unfinalise_ratings')
    
    @property
    def can_edit(self):
        """Can this user edit anything (own content)?"""
        return self.has_any_role(Role.ADMIN, Role.INTERNAL_PANEL, Role.COLLEAGUE)
    
    # ==========================================
    # Helper methods
    # ==========================================
    
    def get_role_display(self):
        """Return comma-separated list of role names"""
        return ", ".join(r.name for r in self.roles.all()) or "No roles"
    
    def add_role(self, role_code):
        """Add a role to this user"""
        try:
            role = Role.objects.get(code=role_code)
            self.roles.add(role)
        except Role.DoesNotExist:
            raise ValueError(f"Role '{role_code}' does not exist")
    
    def remove_role(self, role_code):
        """Remove a role from this user"""
        self.roles.filter(code=role_code).delete()
    
    def set_roles(self, *role_codes):
        """Set user's roles to exactly these roles"""
        self.roles.set(Role.objects.filter(code__in=role_codes))
    
    def clear_roles(self):
        """Remove all roles from this user"""
        self.roles.clear()


class PanelAssignment(models.Model):
    """
    Assignment of outputs to panel members for rating.
    
    Each output can be assigned to multiple panel members.
    Each panel member can be assigned to multiple outputs.
    """
    
    output = models.ForeignKey(
        'Output',  # String reference to avoid circular import
        on_delete=models.CASCADE, 
        related_name='panel_assignments'
    )
    panel_member = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='assignments',
        limit_choices_to={'roles__code': Role.INTERNAL_PANEL}
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='assignments_made'
    )
    
    class Meta:
        unique_together = ['output', 'panel_member']
        verbose_name = "Panel Assignment"
        verbose_name_plural = "Panel Assignments"
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.output} → {self.panel_member.user.username}"


class InternalRating(models.Model):
    """
    Internal panel member rating for an output.
    
    Ratings can be finalised to lock them from further editing.
    Only admins can un-finalise or edit finalised ratings.
    """
    
    class StarRating(models.IntegerChoices):
        UNRATED = 0, 'Not Rated'
        ONE_STAR = 1, '★'
        TWO_STAR = 2, '★★'
        THREE_STAR = 3, '★★★'
        FOUR_STAR = 4, '★★★★'
    
    output = models.ForeignKey(
        'Output',
        on_delete=models.CASCADE, 
        related_name='internal_ratings'
    )
    rater = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='ratings_given'
    )
    
    # Rating fields
    rating = models.IntegerField(
        choices=StarRating.choices, 
        default=StarRating.UNRATED
    )
    comments = models.TextField(
        blank=True,
        help_text="Justification and notes for this rating"
    )
    
    # Finalisation
    is_final = models.BooleanField(
        default=False,
        help_text="Once finalised, only admins can modify"
    )
    finalised_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the rating was finalised"
    )
    
    # Audit trail
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['output', 'rater']
        verbose_name = "Internal Rating"
        verbose_name_plural = "Internal Ratings"
        ordering = ['-created_date']
    
    def __str__(self):
        status = " [FINAL]" if self.is_final else ""
        return f"{self.output}: {self.get_rating_display()} by {self.rater.user.username}{status}"
    
    def finalise(self):
        """Mark this rating as final"""
        if self.rating == self.StarRating.UNRATED:
            raise ValueError("Cannot finalise an unrated output")
        self.is_final = True
        self.finalised_date = timezone.now()
        self.save()
    
    def unfinalise(self):
        """Un-finalise this rating (admin only in practice)"""
        self.is_final = False
        self.finalised_date = None
        self.save()
    
    def can_edit(self, user_profile):
        """
        Check if the given user can edit this rating.
        Uses combined permissions from all user's roles.
        """
        if not user_profile:
            return False
        
        # Can edit any rating? (Admin role)
        if user_profile.can_edit_any_rating:
            return True
        
        # Rating is finalised - only admins can edit
        if self.is_final:
            return False
        
        # Rater can edit their own non-final rating
        return self.rater == user_profile
    
    def can_finalise(self, user_profile):
        """Check if the given user can finalise this rating"""
        if not user_profile:
            return False
        
        # Already final
        if self.is_final:
            return False
        
        # No rating to finalise
        if self.rating == self.StarRating.UNRATED:
            return False
        
        # Admin can finalise any rating
        if user_profile.is_admin:
            return True
        
        # Rater can finalise their own rating
        return self.rater == user_profile


# ==========================================
# Signal handlers for automatic profile creation
# ==========================================

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure UserProfile is saved when User is saved"""
    if hasattr(instance, 'ref_profile'):
        instance.ref_profile.save()
