# core/views_user_management.py
"""
User Management Views for REF-Manager

Provides a user-friendly interface for managing user roles.
Only accessible by users with the 'can_manage_users' permission (Admins).

Usage:
    Add to your urls.py:
    
    from core.views_user_management import (
        UserListView, UserRoleEditView, UserRoleBulkAssignView
    )
    
    urlpatterns = [
        ...
        path('manage/users/', UserListView.as_view(), name='user-list'),
        path('manage/users/<int:pk>/roles/', UserRoleEditView.as_view(), name='user-role-edit'),
        path('manage/users/bulk/', UserRoleBulkAssignView.as_view(), name='user-role-bulk'),
    ]
"""

from django.views.generic import ListView, UpdateView, FormView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django import forms
from django.db.models import Q, Prefetch

from .models_access_control import Role, UserProfile


# =============================================================================
# Permission Mixin
# =============================================================================

class CanManageUsersMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only allow users who can manage users (Admins)"""
    
    def test_func(self):
        if hasattr(self.request.user, 'ref_profile'):
            return self.request.user.ref_profile.can_manage_users
        return False
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to manage users.")
        return redirect('home')


# =============================================================================
# Forms
# =============================================================================

class UserRoleForm(forms.Form):
    """Form for editing a single user's roles"""
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assigned Roles"
    )
    
    def __init__(self, *args, user_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_profile:
            self.fields['roles'].initial = user_profile.roles.all()


class BulkRoleAssignForm(forms.Form):
    """Form for bulk role assignment"""
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        widget=forms.CheckboxSelectMultiple,
        label="Select Users"
    )
    action = forms.ChoiceField(
        choices=[
            ('add', 'Add role to selected users'),
            ('remove', 'Remove role from selected users'),
            ('set', 'Set as only role (replaces existing)'),
        ],
        widget=forms.RadioSelect,
        initial='add',
        label="Action"
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.RadioSelect,
        label="Role"
    )


class QuickRoleForm(forms.Form):
    """Quick form for changing a single user's role inline"""
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        empty_label="-- Select role to add --"
    )


# =============================================================================
# Views
# =============================================================================

class UserListView(CanManageUsersMixin, ListView):
    """List all users with their roles"""
    model = User
    template_name = 'core/user_management/user_list.html'
    context_object_name = 'users'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = User.objects.select_related('ref_profile').prefetch_related(
            Prefetch('ref_profile__roles', queryset=Role.objects.all())
        ).order_by('username')
        
        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Role filter
        role_filter = self.request.GET.get('role', '')
        if role_filter:
            queryset = queryset.filter(ref_profile__roles__code=role_filter)
        
        # No roles filter
        if self.request.GET.get('no_roles'):
            queryset = queryset.filter(ref_profile__roles__isnull=True)
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Role.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['no_roles'] = self.request.GET.get('no_roles', '')
        context['quick_form'] = QuickRoleForm()
        
        # Stats
        context['total_users'] = User.objects.count()
        context['users_without_roles'] = UserProfile.objects.filter(roles__isnull=True).count()
        context['role_counts'] = {
            role.code: role.users.count() 
            for role in Role.objects.all()
        }
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle quick role assignment from list view"""
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        role_code = request.POST.get('role_code')
        
        if user_id and action and role_code:
            try:
                user = User.objects.get(pk=user_id)
                profile, _ = UserProfile.objects.get_or_create(user=user)
                role = Role.objects.get(code=role_code)
                
                if action == 'add':
                    profile.roles.add(role)
                    messages.success(request, f"Added {role.name} to {user.username}")
                elif action == 'remove':
                    profile.roles.remove(role)
                    messages.success(request, f"Removed {role.name} from {user.username}")
            except (User.DoesNotExist, Role.DoesNotExist) as e:
                messages.error(request, str(e))
        
        # Preserve search/filter params
        params = request.GET.urlencode()
        url = reverse('user-list')
        if params:
            url += '?' + params
        return redirect(url)


class UserRoleEditView(CanManageUsersMixin, FormView):
    """Edit roles for a single user"""
    template_name = 'core/user_management/user_role_edit.html'
    form_class = UserRoleForm
    
    def dispatch(self, request, *args, **kwargs):
        self.user_obj = get_object_or_404(User, pk=kwargs['pk'])
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user_obj)
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_profile'] = self.profile
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_obj'] = self.user_obj
        context['profile'] = self.profile
        context['roles'] = Role.objects.all()
        return context
    
    def form_valid(self, form):
        new_roles = form.cleaned_data['roles']
        old_roles = set(self.profile.roles.all())
        
        self.profile.roles.set(new_roles)
        
        # Create message about what changed
        added = set(new_roles) - old_roles
        removed = old_roles - set(new_roles)
        
        if added:
            messages.success(
                self.request, 
                f"Added roles: {', '.join(r.name for r in added)}"
            )
        if removed:
            messages.info(
                self.request, 
                f"Removed roles: {', '.join(r.name for r in removed)}"
            )
        if not added and not removed:
            messages.info(self.request, "No changes made")
        
        return redirect('user-list')


class UserRoleBulkAssignView(CanManageUsersMixin, FormView):
    """Bulk assign roles to multiple users"""
    template_name = 'core/user_management/user_role_bulk.html'
    form_class = BulkRoleAssignForm
    success_url = reverse_lazy('user-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Role.objects.all()
        return context
    
    def form_valid(self, form):
        users = form.cleaned_data['users']
        action = form.cleaned_data['action']
        role = form.cleaned_data['role']
        
        count = 0
        for user in users:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            
            if action == 'add':
                if role not in profile.roles.all():
                    profile.roles.add(role)
                    count += 1
            elif action == 'remove':
                if role in profile.roles.all():
                    profile.roles.remove(role)
                    count += 1
            elif action == 'set':
                profile.roles.set([role])
                count += 1
        
        action_past = {'add': 'Added', 'remove': 'Removed', 'set': 'Set'}
        messages.success(
            self.request,
            f"{action_past[action]} {role.name} for {count} user(s)"
        )
        
        return super().form_valid(form)


# =============================================================================
# Quick Actions (AJAX-friendly)
# =============================================================================

from django.http import JsonResponse
from django.views import View


class QuickRoleToggleView(CanManageUsersMixin, View):
    """Toggle a role on/off for a user (AJAX)"""
    
    def post(self, request, user_id, role_code):
        try:
            user = User.objects.get(pk=user_id)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            role = Role.objects.get(code=role_code)
            
            if role in profile.roles.all():
                profile.roles.remove(role)
                action = 'removed'
                has_role = False
            else:
                profile.roles.add(role)
                action = 'added'
                has_role = True
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'action': action,
                    'has_role': has_role,
                    'message': f"{role.name} {action} for {user.username}"
                })
            else:
                messages.success(request, f"{role.name} {action} for {user.username}")
                return redirect('user-list')
                
        except (User.DoesNotExist, Role.DoesNotExist) as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            else:
                messages.error(request, str(e))
                return redirect('user-list')
