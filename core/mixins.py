# ref_manager/mixins.py
"""
Access Control Mixins for REF-Manager Views

These mixins provide role-based access control for Django class-based views.
They check permissions based on the user's combined roles.

Usage:
    from core.mixins import AdminRequiredMixin, OutputAccessMixin
    
    class MyView(AdminRequiredMixin, ListView):
        # Only admins can access this view
        pass
    
    class OutputListView(OutputAccessMixin, ListView):
        # Automatically filters outputs based on user's permissions
        model = Output
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

# Import Role for role code constants
from .models_access_control import Role


class REFAccessMixin(LoginRequiredMixin):
    """
    Base mixin for REF access control.
    Provides helper method to get user's REF profile.
    """
    
    def get_user_profile(self):
        """Get the current user's REF profile"""
        if hasattr(self.request.user, 'ref_profile'):
            return self.request.user.ref_profile
        return None


class PermissionRequiredMixin(REFAccessMixin, UserPassesTestMixin):
    """
    Generic permission mixin - checks if user has any role granting the permission.
    
    Usage:
        class MyView(PermissionRequiredMixin, View):
            required_permission = 'can_manage_users'
    """
    required_permission = None  # e.g., 'can_manage_users'
    
    def test_func(self):
        if not self.required_permission:
            return True
        profile = self.get_user_profile()
        if not profile:
            return False
        return getattr(profile, self.required_permission, False)


class RoleRequiredMixin(REFAccessMixin, UserPassesTestMixin):
    """
    Require user to have at least one of the specified roles.
    
    Usage:
        class MyView(RoleRequiredMixin, View):
            required_roles = [Role.ADMIN, Role.OBSERVER]
    """
    required_roles = []  # e.g., [Role.ADMIN, Role.OBSERVER]
    
    def test_func(self):
        profile = self.get_user_profile()
        if not profile:
            return False
        return profile.has_any_role(*self.required_roles)


class AdminRequiredMixin(REFAccessMixin, UserPassesTestMixin):
    """Require admin role"""
    
    def test_func(self):
        profile = self.get_user_profile()
        return profile and profile.is_admin


class CanViewAllMixin(REFAccessMixin, UserPassesTestMixin):
    """Require permission to view all outputs (Admin or Observer)"""
    
    def test_func(self):
        profile = self.get_user_profile()
        return profile and profile.can_view_all_outputs


class CanEditMixin(REFAccessMixin, UserPassesTestMixin):
    """Require any role that can create/edit content"""
    
    def test_func(self):
        profile = self.get_user_profile()
        return profile and profile.can_edit


class CanRateMixin(REFAccessMixin, UserPassesTestMixin):
    """Require permission to rate (Admin or Internal Panel)"""
    
    def test_func(self):
        profile = self.get_user_profile()
        return profile and profile.can_rate_assigned


class CanExportMixin(REFAccessMixin, UserPassesTestMixin):
    """Require permission to export data"""
    
    def test_func(self):
        profile = self.get_user_profile()
        return profile and profile.can_export_data


class CanImportMixin(REFAccessMixin, UserPassesTestMixin):
    """Require permission to import data"""
    
    def test_func(self):
        profile = self.get_user_profile()
        return profile and profile.can_import_data


class CanManageUsersMixin(REFAccessMixin, UserPassesTestMixin):
    """Require permission to manage users"""
    
    def test_func(self):
        profile = self.get_user_profile()
        return profile and profile.can_manage_users


class CanAssignPanelMixin(REFAccessMixin, UserPassesTestMixin):
    """Require permission to assign panel members"""
    
    def test_func(self):
        profile = self.get_user_profile()
        return profile and profile.can_assign_panel


class OutputAccessMixin(REFAccessMixin):
    """
    Mixin for output-specific access control.
    Filters queryset based on user's combined role permissions.
    
    Usage:
        class OutputListView(OutputAccessMixin, ListView):
            model = Output
            template_name = 'outputs/list.html'
    """
    
    def get_queryset(self):
        """Filter outputs based on user's combined permissions"""
        # Import here to avoid circular imports
        from .models import Output
        
        profile = self.get_user_profile()
        
        if not profile:
            return Output.objects.none()
        
        # If user can view all outputs (Admin or Observer role)
        if profile.can_view_all_outputs:
            return Output.objects.all()
        
        # Build query for outputs the user can see
        from django.db.models import Q
        
        # Start with empty query
        query = Q(pk__isnull=True)  # Always false - will be OR'd with real conditions
        
        # Own outputs (for Colleague or Internal Panel roles)
        if profile.can_create_outputs:
            query |= Q(owner=profile) | Q(colleague__user_profile=profile)
        
        # Assigned outputs (for Internal Panel role)
        if profile.is_panel_member:
            query |= Q(panel_assignments__panel_member=profile)
        
        return Output.objects.filter(query).distinct()


class OutputViewMixin(OutputAccessMixin):
    """
    Check view permission for a specific output.
    Raises PermissionDenied if user cannot view the output.
    """
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        profile = self.get_user_profile()
        
        if not self._can_view_output(obj, profile):
            raise PermissionDenied("You don't have permission to view this output")
        
        return obj
    
    def _can_view_output(self, output, profile):
        """Check if user can view this output"""
        if not profile:
            return False
        
        # Can view all outputs?
        if profile.can_view_all_outputs:
            return True
        
        # Owner?
        if hasattr(output, 'owner') and output.owner == profile:
            return True
        
        # Linked colleague?
        if hasattr(output, 'colleague') and output.colleague:
            if hasattr(output.colleague, 'user_profile') and output.colleague.user_profile == profile:
                return True
        
        # Assigned panel member?
        if profile.is_panel_member:
            if hasattr(output, 'panel_assignments'):
                return output.panel_assignments.filter(panel_member=profile).exists()
        
        return False


class OutputEditMixin(OutputAccessMixin):
    """
    Check edit permission for a specific output.
    Raises PermissionDenied if user cannot edit the output.
    """
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        profile = self.get_user_profile()
        
        if not self._can_edit_output(obj, profile):
            raise PermissionDenied("You don't have permission to edit this output")
        
        return obj
    
    def _can_edit_output(self, output, profile):
        """Check if user can edit this output"""
        if not profile:
            return False
        
        # Can edit any output? (Admin role)
        if profile.can_edit_any_output:
            return True
        
        # Cannot create outputs = cannot edit own outputs either
        if not profile.can_create_outputs:
            return False
        
        # Owner can edit their own
        if hasattr(output, 'owner') and output.owner == profile:
            return True
        
        # User linked to colleague can edit
        if hasattr(output, 'colleague') and output.colleague:
            if hasattr(output.colleague, 'user_profile') and output.colleague.user_profile == profile:
                return True
        
        return False


class OutputDeleteMixin(OutputAccessMixin):
    """
    Check delete permission for a specific output.
    Raises PermissionDenied if user cannot delete the output.
    """
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        profile = self.get_user_profile()
        
        if not profile or not profile.can_delete_any_output:
            raise PermissionDenied("You don't have permission to delete this output")
        
        return obj


class RatingAccessMixin(REFAccessMixin):
    """
    Mixin for rating-specific access control.
    Provides methods to check if user can rate or edit ratings.
    """
    
    def can_rate_output(self, output):
        """Check if current user can rate this output"""
        profile = self.get_user_profile()
        
        if not profile:
            return False
        
        # Admin can rate anything
        if profile.is_admin:
            return True
        
        # Must have rating permission
        if not profile.can_rate_assigned:
            return False
        
        # Panel members can rate if assigned
        if profile.is_panel_member:
            if hasattr(output, 'panel_assignments'):
                return output.panel_assignments.filter(panel_member=profile).exists()
        
        return False
    
    def can_edit_rating(self, rating):
        """Check if current user can edit this rating"""
        profile = self.get_user_profile()
        if not profile:
            return False
        return rating.can_edit(profile)
    
    def can_finalise_rating(self, rating):
        """Check if current user can finalise this rating"""
        profile = self.get_user_profile()
        if not profile:
            return False
        return rating.can_finalise(profile)


class ColleagueAccessMixin(REFAccessMixin):
    """
    Mixin for colleague-specific access control.
    Filters colleague queryset based on user's permissions.
    """
    
    def get_queryset(self):
        """Filter colleagues based on user's permissions"""
        from .models import Colleague
        
        profile = self.get_user_profile()
        
        if not profile:
            return Colleague.objects.none()
        
        # Can view all colleagues?
        if profile.can_view_all_colleagues:
            return Colleague.objects.all()
        
        # Otherwise only see own colleague record
        if profile.linked_colleague:
            return Colleague.objects.filter(pk=profile.linked_colleague.pk)
        
        return Colleague.objects.none()


class PanelAssignmentAccessMixin(REFAccessMixin):
    """
    Mixin for panel assignment access control.
    Only admins and panel assigners can manage assignments.
    """
    
    def get_queryset(self):
        """Filter assignments based on user's permissions"""
        from .models_access_control import PanelAssignment
        
        profile = self.get_user_profile()
        
        if not profile:
            return PanelAssignment.objects.none()
        
        # Admins and panel assigners can see all
        if profile.can_assign_panel:
            return PanelAssignment.objects.all()
        
        # Panel members can see their own assignments
        if profile.is_panel_member:
            return PanelAssignment.objects.filter(panel_member=profile)
        
        return PanelAssignment.objects.none()


class InternalRatingAccessMixin(REFAccessMixin):
    """
    Mixin for internal rating access control.
    Filters ratings based on user's permissions.
    """
    
    def get_queryset(self):
        """Filter ratings based on user's permissions"""
        from .models_access_control import InternalRating
        
        profile = self.get_user_profile()
        
        if not profile:
            return InternalRating.objects.none()
        
        # Can view all ratings?
        if profile.can_view_all_ratings:
            return InternalRating.objects.all()
        
        # Panel members can see their own ratings
        if profile.is_panel_member:
            return InternalRating.objects.filter(rater=profile)
        
        # Colleagues can see ratings on their own outputs
        if profile.linked_colleague:
            return InternalRating.objects.filter(
                output__colleague=profile.linked_colleague
            )
        
        return InternalRating.objects.none()
