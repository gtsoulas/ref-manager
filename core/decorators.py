# ref_manager/decorators.py
"""
Access Control Decorators for REF-Manager Views

These decorators provide role-based access control for Django function-based views.
They check permissions based on the user's combined roles.

Usage:
    from core.decorators import admin_required, permission_required
    
    @admin_required
    def my_admin_view(request):
        # Only admins can access this view
        pass
    
    @permission_required('can_export_data')
    def export_view(request):
        # Only users with export permission can access
        pass
    
    @roles_required(Role.ADMIN, Role.OBSERVER)
    def readonly_admin_view(request):
        # Admins and observers can access
        pass
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages

# Import Role for role code constants
from .models_access_control import Role


def roles_required(*role_codes):
    """
    Decorator requiring user to have at least one of the specified roles.
    
    Usage:
        @roles_required(Role.ADMIN, Role.OBSERVER)
        def my_view(request):
            ...
    
    Args:
        *role_codes: One or more role codes (e.g., Role.ADMIN, Role.OBSERVER)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('login')
            
            profile = getattr(request.user, 'ref_profile', None)
            if not profile or not profile.has_any_role(*role_codes):
                return HttpResponseForbidden(
                    "You don't have permission to access this page. "
                    f"Required role: {', '.join(str(r) for r in role_codes)}"
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permission_required(permission_name):
    """
    Decorator requiring user to have a specific permission 
    (from any of their roles).
    
    Usage:
        @permission_required('can_manage_users')
        def my_view(request):
            ...
    
    Args:
        permission_name: Name of the permission property (e.g., 'can_manage_users')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('login')
            
            profile = getattr(request.user, 'ref_profile', None)
            if not profile or not getattr(profile, permission_name, False):
                return HttpResponseForbidden(
                    f"You don't have permission to access this page. "
                    f"Required permission: {permission_name}"
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator requiring admin role.
    
    Usage:
        @admin_required
        def admin_only_view(request):
            ...
    """
    return roles_required(Role.ADMIN)(view_func)


def can_edit_required(view_func):
    """
    Decorator requiring permission to edit (Admin, Internal Panel, or Colleague).
    
    Usage:
        @can_edit_required
        def create_output_view(request):
            ...
    """
    return roles_required(Role.ADMIN, Role.INTERNAL_PANEL, Role.COLLEAGUE)(view_func)


def can_view_all_required(view_func):
    """
    Decorator requiring permission to view all (Admin or Observer).
    
    Usage:
        @can_view_all_required
        def all_outputs_view(request):
            ...
    """
    return roles_required(Role.ADMIN, Role.OBSERVER)(view_func)


def panel_or_admin_required(view_func):
    """
    Decorator requiring panel member or admin role.
    
    Usage:
        @panel_or_admin_required
        def rating_view(request):
            ...
    """
    return roles_required(Role.ADMIN, Role.INTERNAL_PANEL)(view_func)


def observer_or_admin_required(view_func):
    """
    Decorator requiring observer or admin role.
    
    Usage:
        @observer_or_admin_required
        def reports_view(request):
            ...
    """
    return roles_required(Role.ADMIN, Role.OBSERVER)(view_func)


# ==========================================
# Object-level permission decorators
# ==========================================

def output_view_permission(view_func):
    """
    Decorator checking if user can view the specified output.
    Expects 'pk' or 'output_pk' in URL kwargs.
    
    Usage:
        @output_view_permission
        def output_detail_view(request, pk):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import Output
        
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get output
        pk = kwargs.get('pk') or kwargs.get('output_pk')
        try:
            output = Output.objects.get(pk=pk)
        except Output.DoesNotExist:
            from django.http import Http404
            raise Http404("Output not found")
        
        profile = getattr(request.user, 'ref_profile', None)
        if not profile:
            return HttpResponseForbidden("No user profile found")
        
        # Check view permission
        can_view = False
        
        if profile.can_view_all_outputs:
            can_view = True
        elif hasattr(output, 'owner') and output.owner == profile:
            can_view = True
        elif hasattr(output, 'colleague') and output.colleague:
            if hasattr(output.colleague, 'user_profile') and output.colleague.user_profile == profile:
                can_view = True
        elif profile.is_panel_member:
            if hasattr(output, 'panel_assignments'):
                can_view = output.panel_assignments.filter(panel_member=profile).exists()
        
        if not can_view:
            return HttpResponseForbidden("You don't have permission to view this output")
        
        # Add output to request for convenience
        request.output = output
        return view_func(request, *args, **kwargs)
    
    return wrapper


def output_edit_permission(view_func):
    """
    Decorator checking if user can edit the specified output.
    Expects 'pk' or 'output_pk' in URL kwargs.
    
    Usage:
        @output_edit_permission
        def output_edit_view(request, pk):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import Output
        
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get output
        pk = kwargs.get('pk') or kwargs.get('output_pk')
        try:
            output = Output.objects.get(pk=pk)
        except Output.DoesNotExist:
            from django.http import Http404
            raise Http404("Output not found")
        
        profile = getattr(request.user, 'ref_profile', None)
        if not profile:
            return HttpResponseForbidden("No user profile found")
        
        # Check edit permission
        can_edit = False
        
        if profile.can_edit_any_output:
            can_edit = True
        elif profile.can_create_outputs:
            if hasattr(output, 'owner') and output.owner == profile:
                can_edit = True
            elif hasattr(output, 'colleague') and output.colleague:
                if hasattr(output.colleague, 'user_profile') and output.colleague.user_profile == profile:
                    can_edit = True
        
        if not can_edit:
            return HttpResponseForbidden("You don't have permission to edit this output")
        
        # Add output to request for convenience
        request.output = output
        return view_func(request, *args, **kwargs)
    
    return wrapper


def rating_edit_permission(view_func):
    """
    Decorator checking if user can edit the specified rating.
    Expects 'pk' or 'rating_pk' in URL kwargs.
    
    Usage:
        @rating_edit_permission
        def rating_edit_view(request, pk):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models_access_control import InternalRating
        
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get rating
        pk = kwargs.get('pk') or kwargs.get('rating_pk')
        try:
            rating = InternalRating.objects.get(pk=pk)
        except InternalRating.DoesNotExist:
            from django.http import Http404
            raise Http404("Rating not found")
        
        profile = getattr(request.user, 'ref_profile', None)
        if not profile:
            return HttpResponseForbidden("No user profile found")
        
        # Check edit permission
        if not rating.can_edit(profile):
            if rating.is_final:
                return HttpResponseForbidden(
                    "This rating has been finalised and cannot be changed"
                )
            return HttpResponseForbidden("You don't have permission to edit this rating")
        
        # Add rating to request for convenience
        request.rating = rating
        return view_func(request, *args, **kwargs)
    
    return wrapper


def can_rate_output(view_func):
    """
    Decorator checking if user can rate the specified output.
    Expects 'pk' or 'output_pk' in URL kwargs.
    
    Usage:
        @can_rate_output
        def add_rating_view(request, output_pk):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import Output
        
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Get output
        pk = kwargs.get('pk') or kwargs.get('output_pk')
        try:
            output = Output.objects.get(pk=pk)
        except Output.DoesNotExist:
            from django.http import Http404
            raise Http404("Output not found")
        
        profile = getattr(request.user, 'ref_profile', None)
        if not profile:
            return HttpResponseForbidden("No user profile found")
        
        # Check rating permission
        can_rate = False
        
        if profile.is_admin:
            can_rate = True
        elif profile.can_rate_assigned and profile.is_panel_member:
            if hasattr(output, 'panel_assignments'):
                can_rate = output.panel_assignments.filter(panel_member=profile).exists()
        
        if not can_rate:
            return HttpResponseForbidden("You are not assigned to rate this output")
        
        # Add output to request for convenience
        request.output = output
        return view_func(request, *args, **kwargs)
    
    return wrapper
