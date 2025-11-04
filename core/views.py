from collections import defaultdict
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.core.mail import send_mail
from .models import (
    Colleague, Output, CriticalFriend, CriticalFriendAssignment,
    Request, InternalReview, InternalPanelMember, InternalPanelAssignment, Task
)
from .forms import (
    ColleagueForm, OutputForm, CriticalFriendForm, AssignmentForm,
    RequestForm, InternalReviewForm, OutputFilterForm, TaskForm
)

from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils.dateparse import parse_date as django_parse_date, parse_datetime
from core.models import Colleague, Output
from .import_forms import CSVUploadForm
import csv
import io
import re
from datetime import datetime, date

User = get_user_model()


def is_admin(user):
    return user.is_staff or user.groups.filter(name='Department Admin').exists()


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')


@login_required
def dashboard(request):
    total_colleagues = Colleague.objects.filter(is_returnable=True).count()
    independent_count = Colleague.objects.filter(colleague_category='independent').count()
    non_independent_count = Colleague.objects.filter(colleague_category='non_independent').count()
    postdoc_count = Colleague.objects.filter(colleague_category='postdoc').count()
    academic_count = Colleague.objects.filter(colleague_category='academic').count()
    research_assistant_count = Colleague.objects.filter(colleague_category='research_assistant').count()
    support_count = Colleague.objects.filter(colleague_category='support').count()
    current_staff = Colleague.objects.filter(employment_status='current').count()
    former_staff = Colleague.objects.filter(employment_status='former').count()
    
    total_outputs = Output.objects.count()
    approved_outputs = Output.objects.filter(status='approved').count()
    outputs_in_review = Output.objects.filter(
        status__in=['internal-review', 'external-review']
    ).count()
    pending_requests = Request.objects.filter(status='pending').count()
    
    quality_distribution = Output.objects.filter(
        status='approved',
        quality_rating__isnull=False
    ).values('quality_rating').annotate(count=Count('id'))
    
    quality_profile = {'4*': 0, '3*': 0, '2*': 0, '1*': 0, 'U': 0}
    total_rated = sum(q['count'] for q in quality_distribution)
    
    if total_rated > 0:
        for q in quality_distribution:
            rating = q['quality_rating']
            percentage = (q['count'] / total_rated) * 100
            quality_profile[rating] = round(percentage, 1)
    
    recent_outputs = Output.objects.select_related('colleague').order_by('-updated_at')[:5]
    recent_reviews = CriticalFriendAssignment.objects.select_related(
        'output', 'critical_friend'
    ).order_by('-assigned_date')[:5]
    
    critical_friends_count = CriticalFriend.objects.count()
    active_cf_assignments = CriticalFriendAssignment.objects.filter(
        status__in=['assigned', 'accepted', 'in-progress']
    ).count()
    
    overdue_assignments = CriticalFriendAssignment.objects.filter(
        status__in=['assigned', 'accepted', 'in-progress'],
        due_date__lt=timezone.now().date()
    ).count()

    internal_panel_count = InternalPanelMember.objects.filter(is_active=True).count()
    active_panel_assignments = InternalPanelAssignment.objects.filter(
        status__in=['assigned', 'in_progress']
    ).count()
    
    overdue_panel_assignments = InternalPanelAssignment.objects.filter(
        status__in=['assigned', 'in_progress'],
        review_date__isnull=False,
        review_date__lt=timezone.now().date()
    ).count()
    
    overdue_requests = Request.objects.filter(
        status__in=['pending', 'in-progress'],
        deadline__lt=timezone.now().date()
    ).count()

    overdue_requests = Request.objects.filter(
        status__in=['pending', 'in-progress'],
        deadline__lt=timezone.now().date()
    ).count()
    
    context = {
        'total_colleagues': total_colleagues,
        'total_outputs': total_outputs,
        'approved_outputs': approved_outputs,
        'outputs_in_review': outputs_in_review,
        'pending_requests': pending_requests,
        'quality_profile': quality_profile,
        'recent_outputs': recent_outputs,
        'recent_reviews': recent_reviews,
        'critical_friends_count': critical_friends_count,
        'active_cf_assignments': active_cf_assignments,
        'overdue_assignments': overdue_assignments,
        'overdue_requests': overdue_requests,
         'internal_panel_count': internal_panel_count,
        'active_panel_assignments': active_panel_assignments,
        'overdue_panel_assignments': overdue_panel_assignments,
    }
    
    return render(request, 'core/dashboard.html', context)



@login_required
def colleague_detail(request, pk):
    colleague = get_object_or_404(Colleague.objects.select_related('user'), pk=pk)
    outputs = colleague.outputs.all().order_by('-publication_date')
    is_own_profile = request.user == colleague.user
    
    return render(request, 'core/colleague_detail.html', {
        'colleague': colleague,
        'outputs': outputs,
        'is_own_profile': is_own_profile,
    })


@login_required
@user_passes_test(is_admin)
def colleague_create(request):
    if request.method == 'POST':
        form = ColleagueForm(request.POST)
        if form.is_valid():
            colleague = form.save()
            messages.success(request, f'Colleague {colleague} created successfully')
            return redirect('colleague_detail', pk=colleague.pk)
    else:
        form = ColleagueForm()
    
    return render(request, 'core/colleague_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def colleague_update(request, pk):
    colleague = get_object_or_404(Colleague, pk=pk)
    
    if request.method == 'POST':
        form = ColleagueForm(request.POST, instance=colleague)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colleague updated successfully')
            return redirect('colleague_detail', pk=colleague.pk)
    else:
        form = ColleagueForm(instance=colleague)
    
    return render(request, 'core/colleague_form.html', {
        'form': form, 'colleague': colleague, 'action': 'Update'
    })


@login_required
@user_passes_test(is_admin)
def colleague_mark_as_former(request, pk):
    """Mark a colleague as former staff (instead of deleting)"""
    colleague = get_object_or_404(Colleague, pk=pk)
    
    if request.method == 'POST':
        colleague.employment_status = 'former'
        if not colleague.employment_end_date:
            colleague.employment_end_date = timezone.now().date()
        colleague.save()
        
        messages.success(
            request,
            f'{colleague.user.get_full_name()} marked as former staff.'
        )
        return redirect('colleague_detail', pk=colleague.pk)
    
    context = {
        'colleague': colleague,
    }
    
    return render(request, 'core/colleague_mark_former.html', context)


@login_required
def output_list(request):
    outputs = Output.objects.select_related('colleague__user').all()
    
    filter_form = OutputFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        quality = filter_form.cleaned_data.get('quality_rating')
        uoa = filter_form.cleaned_data.get('uoa')
        colleague_id = filter_form.cleaned_data.get('colleague')
        
        if status:
            outputs = outputs.filter(status=status)
        if quality:
            outputs = outputs.filter(quality_rating=quality)
        if uoa:
            outputs = outputs.filter(uoa__icontains=uoa)
        if colleague_id:
            outputs = outputs.filter(colleague_id=colleague_id)
    
    search_query = request.GET.get('search', '')
    if search_query:
        outputs = outputs.filter(
            Q(title__icontains=search_query) |
            Q(all_authors__icontains=search_query) |
            Q(publication_venue__icontains=search_query)
        )
    
    outputs = outputs.order_by('-publication_date')
    
    return render(request, 'core/output_list.html', {
        'outputs': outputs,
        'filter_form': filter_form,
        'search_query': search_query,
    })


@login_required
def output_detail(request, pk):
    output = get_object_or_404(Output.objects.select_related('colleague__user'), pk=pk)
    internal_reviews = output.internal_reviews.select_related('reviewer').all()
    critical_friend_reviews = output.critical_friend_reviews.select_related('critical_friend').all()
    
    is_owner = request.user == output.colleague.user
    can_edit = is_owner or is_admin(request.user)
    
    return render(request, 'core/output_detail.html', {
        'output': output,
        'internal_reviews': internal_reviews,
        'critical_friend_reviews': critical_friend_reviews,
        'is_owner': is_owner,
        'can_edit': can_edit,
    })


@login_required
def output_create(request):
    if request.method == 'POST':
        form = OutputForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            output = form.save(commit=False)
            
            if not is_admin(request.user):
                colleague = get_object_or_404(Colleague, user=request.user)
                output.colleague = colleague
            
            output.save()
            messages.success(request, 'Output created successfully')
            return redirect('output_detail', pk=output.pk)
    else:
        form = OutputForm(user=request.user)
    
    return render(request, 'core/output_form.html', {'form': form, 'action': 'Create'})


@login_required
def output_update(request, pk):
    output = get_object_or_404(Output, pk=pk)
    
    is_owner = request.user == output.colleague.user
    can_edit = is_owner or is_admin(request.user)
    
    if not can_edit:
        messages.error(request, 'You do not have permission to edit this output')
        return redirect('output_detail', pk=pk)
    
    if request.method == 'POST':
        form = OutputForm(request.POST, request.FILES, instance=output, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Output updated successfully')
            return redirect('output_detail', pk=pk)
    else:
        form = OutputForm(instance=output, user=request.user)
    
    return render(request, 'core/output_form.html', {
        'form': form, 'output': output, 'action': 'Update'
    })


@login_required
@user_passes_test(is_admin)
def output_delete(request, pk):
    output = get_object_or_404(Output, pk=pk)
    
    if request.method == 'POST':
        output.delete()
        messages.success(request, 'Output deleted successfully')
        return redirect('output_list')
    
    return render(request, 'core/output_confirm_delete.html', {'output': output})


@login_required
def critical_friend_list(request):
    critical_friends = CriticalFriend.objects.all().order_by('name')
    
    return render(request, 'core/critical_friend_list.html', {
        'critical_friends': critical_friends
    })


@login_required
def critical_friend_detail(request, pk):
    cf = get_object_or_404(CriticalFriend, pk=pk)
    assignments = cf.assignments.select_related('output__colleague__user').order_by('-assigned_date')
    
    return render(request, 'core/critical_friend_detail.html', {
        'critical_friend': cf,
        'assignments': assignments,
    })


@login_required
@user_passes_test(is_admin)
def critical_friend_create(request):
    if request.method == 'POST':
        form = CriticalFriendForm(request.POST)
        if form.is_valid():
            cf = form.save()
            messages.success(request, f'Critical friend {cf.name} added successfully')
            return redirect('critical_friend_detail', pk=cf.pk)
    else:
        form = CriticalFriendForm()
    
    return render(request, 'core/critical_friend_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def critical_friend_update(request, pk):
    cf = get_object_or_404(CriticalFriend, pk=pk)
    
    if request.method == 'POST':
        form = CriticalFriendForm(request.POST, instance=cf)
        if form.is_valid():
            form.save()
            messages.success(request, 'Critical friend updated successfully')
            return redirect('critical_friend_detail', pk=pk)
    else:
        form = CriticalFriendForm(instance=cf)
    
    return render(request, 'core/critical_friend_form.html', {
        'form': form, 'critical_friend': cf, 'action': 'Update'
    })



@login_required
@user_passes_test(is_admin)
def assign_critical_friend(request, output_id):
    output = get_object_or_404(Output, pk=output_id)
    
    if request.method == 'POST':
        critical_friend_id = request.POST.get('critical_friend')
        due_date = request.POST.get('due_date')
        notes = request.POST.get('notes', '')
        
        critical_friend = get_object_or_404(CriticalFriend, pk=critical_friend_id)
        
        # Create assignment
        assignment = CriticalFriendAssignment.objects.create(
            output=output,
            critical_friend=critical_friend,
            due_date=due_date if due_date else None,
            notes=notes,
            status='assigned'
        )
        
        messages.success(request, f'Successfully assigned to {critical_friend.name}')
        return redirect('output_detail', pk=output_id)
    
    # GET request - show form
    critical_friends = CriticalFriend.objects.filter(availability='available')
    
    context = {
        'output': output,
        'critical_friends': critical_friends,
    }
    
    return render(request, 'core/assign_critical_friend.html', context)




@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(
        CriticalFriendAssignment.objects.select_related('output', 'critical_friend'),
        pk=pk
    )
    
    is_assigned_cf = (
        hasattr(request.user, 'critical_friend_profile') and
        request.user.critical_friend_profile == assignment.critical_friend
    )
    can_view = is_assigned_cf or is_admin(request.user)
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this assignment')
        return redirect('dashboard')
    
    return render(request, 'core/assignment_detail.html', {
        'assignment': assignment,
        'is_assigned_cf': is_assigned_cf,
    })


@login_required
def submit_review(request, assignment_pk):
    assignment = get_object_or_404(CriticalFriendAssignment, pk=assignment_pk)
    
    is_assigned_cf = (
        hasattr(request.user, 'critical_friend_profile') and
        request.user.critical_friend_profile == assignment.critical_friend
    )
    
    if not is_assigned_cf:
        messages.error(request, 'You are not assigned to review this output')
        return redirect('dashboard')
    
    if request.method == 'POST':
        from .forms import ReviewResponseForm
        form = ReviewResponseForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review submitted successfully')
            return redirect('assignment_detail', pk=assignment_pk)
    else:
        from .forms import ReviewResponseForm
        form = ReviewResponseForm(instance=assignment)
    
    return render(request, 'core/submit_review.html', {
        'form': form,
        'assignment': assignment,
    })


@login_required
def request_list(request):
    requests = Request.objects.select_related('assigned_to', 'created_by').order_by('-created_at')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    return render(request, 'core/request_list.html', {
        'requests': requests,
        'status_filter': status_filter,
    })


@login_required
def request_detail(request, pk):
    req = get_object_or_404(Request, pk=pk)
    
    return render(request, 'core/request_detail.html', {'request': req})


@login_required
@user_passes_test(is_admin)
def request_create(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.created_by = request.user
            req.save()
            messages.success(request, 'Request created successfully')
            return redirect('request_detail', pk=req.pk)
    else:
        form = RequestForm()
    
    return render(request, 'core/request_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def request_update(request, pk):
    req = get_object_or_404(Request, pk=pk)
    
    if request.method == 'POST':
        form = RequestForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, 'Request updated successfully')
            return redirect('request_detail', pk=pk)
    else:
        form = RequestForm(instance=req)
    
    return render(request, 'core/request_form.html', {
        'form': form, 'request': req, 'action': 'Update'
    })


@login_required
@user_passes_test(is_admin)
def output_change_status(request, pk):
    output = get_object_or_404(Output, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Output.STATUS_CHOICES):
            output.status = new_status
            
            if new_status == 'approved':
                output.approved_date = timezone.now()
            
            output.save()
            messages.success(request, f'Output status changed to {output.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
        
        return redirect('output_detail', pk=pk)
    
    return render(request, 'core/output_change_status.html', {
        'output': output,
        'status_choices': Output.STATUS_CHOICES,
    })


@login_required
@user_passes_test(is_admin)
def add_internal_review(request, output_pk):
    output = get_object_or_404(Output, pk=output_pk)
    
    if request.method == 'POST':
        form = InternalReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.output = output
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Internal review added successfully')
            return redirect('output_detail', pk=output_pk)
    else:
        form = InternalReviewForm()
    
    return render(request, 'core/add_internal_review.html', {
        'form': form,
        'output': output,
    })


@login_required
@user_passes_test(is_admin)
def bulk_upload_outputs(request):
    if request.method == 'POST':
        from .forms import BulkUploadForm
        import csv
        import io
        
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            colleague = form.cleaned_data['colleague']
            csv_file = request.FILES['csv_file']
            
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            created_count = 0
            for row in reader:
                try:
                    Output.objects.create(
                        colleague=colleague,
                        title=row['title'],
                        publication_type=row['publication_type'],
                        publication_date=row['publication_date'],
                        publication_venue=row.get('publication_venue', ''),
                        all_authors=row['all_authors'],
                        author_position=int(row['author_position']),
                        uoa=row['uoa'],
                    )
                    created_count += 1
                except Exception as e:
                    messages.warning(request, f'Error importing row: {str(e)}')
            
            messages.success(request, f'Successfully imported {created_count} outputs')
            return redirect('colleague_detail', pk=colleague.pk)
    else:
        from .forms import BulkUploadForm
        form = BulkUploadForm()
    
    return render(request, 'core/bulk_upload.html', {'form': form})


@login_required
def reports_dashboard(request):
    """Main reports dashboard"""
    return render(request, 'core/reports_dashboard.html')


@login_required
def colleague_outputs_report(request):
    """Report showing outputs per colleague"""
    colleagues = Colleague.objects.select_related('user').annotate(
        total_outputs=Count('outputs'),
        approved_outputs=Count('outputs', filter=Q(outputs__status='approved'))
    ).order_by('user__last_name')
    
    return render(request, 'core/colleague_outputs_report.html', {
        'colleagues': colleagues
    })


@login_required
def quality_profile_report(request):
    """Report showing quality distribution"""
    quality_dist = Output.objects.filter(
        status='approved',
        quality_rating__isnull=False
    ).values('quality_rating').annotate(count=Count('id')).order_by('quality_rating')
    
    return render(request, 'core/quality_profile_report.html', {
        'quality_distribution': quality_dist
    })


@login_required
def uoa_report(request):
    """Report by Unit of Assessment"""
    uoa_stats = Colleague.objects.values('unit_of_assessment').annotate(
        colleague_count=Count('id'),
        output_count=Count('outputs'),
        approved_count=Count('outputs', filter=Q(outputs__status='approved'))
    ).order_by('unit_of_assessment')
    
    return render(request, 'core/uoa_report.html', {
        'uoa_stats': uoa_stats
    })


@login_required
def internal_panel_list(request):
    """List all internal panel members"""
    panel_members = InternalPanelMember.objects.all().select_related('colleague__user')
    return render(request, 'core/internal_panel_list.html', {
        'panel_members': panel_members
    })


@login_required
def internal_panel_detail(request, pk):
    """View internal panel member details"""
    panel_member = get_object_or_404(InternalPanelMember, pk=pk)
    assignments = panel_member.internalpanelassignment_set.all().select_related('output')
    return render(request, 'core/internal_panel_detail.html', {
        'panel_member': panel_member,
        'assignments': assignments,
    })


@login_required
@user_passes_test(is_admin)
def internal_panel_create(request):
    """Create new internal panel member"""
    from .forms import InternalPanelMemberForm
    if request.method == 'POST':
        form = InternalPanelMemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Internal panel member added successfully.')
            return redirect('internal_panel_list')
    else:
        form = InternalPanelMemberForm()
    
    return render(request, 'core/internal_panel_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def internal_panel_update(request, pk):
    """Update internal panel member"""
    from .forms import InternalPanelMemberForm
    panel_member = get_object_or_404(InternalPanelMember, pk=pk)
    if request.method == 'POST':
        form = InternalPanelMemberForm(request.POST, instance=panel_member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Internal panel member updated successfully.')
            return redirect('internal_panel_detail', pk=pk)
    else:
        form = InternalPanelMemberForm(instance=panel_member)
    
    return render(request, 'core/internal_panel_form.html', {
        'form': form,
        'panel_member': panel_member
    })


@login_required
@user_passes_test(is_admin)
def assign_internal_panel(request, output_pk):
    """Assign internal panel member to output"""
    from .forms import InternalPanelAssignmentForm
    output = get_object_or_404(Output, pk=output_pk)
    
    if request.method == 'POST':
        form = InternalPanelAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.output = output
            assignment.save()
            messages.success(request, 'Internal panel member assigned successfully.')
            return redirect('output_detail', pk=output_pk)
    else:
        form = InternalPanelAssignmentForm()
    
    return render(request, 'core/assign_internal_panel.html', {
        'form': form,
        'output': output,
    })


@login_required
@user_passes_test(is_admin)
def internal_panel_assignment_update(request, pk):
    """Update internal panel assignment"""
    from .forms import InternalPanelAssignmentForm
    assignment = get_object_or_404(InternalPanelAssignment, pk=pk)
    
    if request.method == 'POST':
        form = InternalPanelAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully.')
            return redirect('output_detail', pk=assignment.output.pk)
    else:
        form = InternalPanelAssignmentForm(instance=assignment)
    
    return render(request, 'core/internal_panel_assignment_form.html', {
        'form': form,
        'assignment': assignment,
    })
@login_required
def task_list(request):
    """Display list of all tasks with filtering"""
    tasks = Task.objects.select_related('assigned_to', 'created_by')
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    assigned_filter = request.GET.get('assigned', '')
    search_query = request.GET.get('q', '')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if category_filter:
        tasks = tasks.filter(category=category_filter)
    if assigned_filter:
        tasks = tasks.filter(assigned_to_id=assigned_filter)
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Get filter options
    users = User.objects.filter(assigned_tasks__isnull=False).distinct()
    
    # Calculate statistics
    stats = {
        'total': Task.objects.count(),
        'pending': Task.objects.filter(status='pending').count(),
        'in_progress': Task.objects.filter(status='in_progress').count(),
        'completed': Task.objects.filter(status='completed').count(),
        'overdue': Task.objects.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now().date()
        ).count(),
    }
    
    context = {
        'tasks': tasks,
        'stats': stats,
        'users': users,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'assigned_filter': assigned_filter,
        'search_query': search_query,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'category_choices': Task.CATEGORY_CHOICES,
    }
    
    return render(request, 'core/task_list.html', context)


@login_required
def task_detail(request, pk):
    """Display task details"""
    task = get_object_or_404(
        Task.objects.select_related('assigned_to', 'created_by'),
        pk=pk
    )
    
    context = {
        'task': task,
    }
    
    return render(request, 'core/task_detail.html', context)


@login_required
def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'core/task_form.html', context)


@login_required
def task_update(request, pk):
    """Update an existing task"""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'action': 'Update',
    }
    
    return render(request, 'core/task_form.html', context)


@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('task_list')
    
    context = {
        'task': task,
    }
    
    return render(request, 'core/task_confirm_delete.html', context)


@login_required
def task_complete(request, pk):
    """Mark a task as completed"""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task.mark_completed()
        messages.success(request, f'Task "{task.title}" marked as completed!')
        return redirect('task_detail', pk=task.pk)
    
    return redirect('task_detail', pk=pk)


@login_required
def task_dashboard(request):
    """Dashboard view for tasks"""
    # Get user's tasks
    my_tasks = Task.objects.filter(assigned_to=request.user).exclude(status='completed')
    
    # Get overdue tasks
    overdue_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=timezone.now().date()
    ).select_related('assigned_to')
    
    # Get upcoming tasks (due in next 7 days)
    upcoming_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__gte=timezone.now().date(),
        due_date__lte=timezone.now().date() + timezone.timedelta(days=7)
    ).select_related('assigned_to')
    
    # Get recent activity
    recent_tasks = Task.objects.select_related('assigned_to', 'created_by').order_by('-updated_at')[:10]
    
    # Statistics by category
    category_stats = Task.objects.values('category').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Statistics by priority
    priority_stats = Task.objects.values('priority').annotate(
        total=Count('id')
    ).order_by('priority')
    
    context = {
        'my_tasks': my_tasks,
        'overdue_tasks': overdue_tasks,
        'upcoming_tasks': upcoming_tasks,
        'recent_tasks': recent_tasks,
        'category_stats': category_stats,
        'priority_stats': priority_stats,
    }
    
    return render(request, 'core/task_dashboard.html', context)


@login_required
def request_complete(request, pk):
    """Mark a request as completed"""
    req = get_object_or_404(Request, pk=pk)
    
    if request.method == 'POST':
        req.status = 'completed'
        req.completed_at = timezone.now()
        req.save()
        messages.success(request, f'Request "{req.subject}" marked as completed!')
        return redirect('request_list')
    
    context = {
        'request': req,
    }
    
    return render(request, 'core/request_confirm_complete.html', context)


@login_required
def request_delete(request, pk):
    """Delete a request"""
    req = get_object_or_404(Request, pk=pk)
    
    if request.method == 'POST':
        subject = req.subject
        req.delete()
        messages.success(request, f'Request "{subject}" deleted successfully!')
        return redirect('request_list')
    
    context = {
        'request': req,
    }
    
    return render(request, 'core/request_confirm_delete.html', context)

def parse_authors(person_string):
    """
    Parse the Person field which can contain multiple authors separated by //
    Returns a list of author names
    """
    if not person_string:
        return []
    
    # Split by // and clean up
    authors = [author.strip() for author in person_string.split('//')]
    return [author for author in authors if author]


def find_or_create_colleague(author_name, create_if_missing=True):
    """
    Find a colleague by name, or create one (with User account) if allowed
    Handles various name formats
    """
    if not author_name:
        return None
    
    # Try to extract last name (usually in UPPERCASE in CSV)
    parts = author_name.split(',')
    if len(parts) >= 2:
        last_name = parts[0].strip()
        first_names = parts[1].strip()
    else:
        # Fallback: split by spaces
        name_parts = author_name.split()
        if name_parts:
            last_name = name_parts[-1]
            first_names = ' '.join(name_parts[:-1])
        else:
            return None
    
    # Try to find existing colleague by staff_id
    colleague = Colleague.objects.filter(staff_id__iexact=last_name[:20]).first()
    
    if not colleague:
        # Try searching by linked User's last name
        colleague = Colleague.objects.filter(
            user__last_name__iexact=last_name
        ).first()
    
    if colleague:
        return colleague
    
    # If not found and we're allowed to create
    if create_if_missing:
        try:
            # Create a username from the name (make it unique)
            if first_names:
                first_part = first_names.split()[0].lower()
            else:
                first_part = 'user'
            
            base_username = f"{first_part}.{last_name.lower()}"
            # Clean username - remove special characters
            base_username = re.sub(r'[^a-z0-9._-]', '', base_username)[:30]
            
            # Make username unique if it already exists
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create email
            email = f"{username}@york.ac.uk"
            
            # Create User account first (required for Colleague)
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_names[:150] if first_names else '',
                last_name=last_name[:150],
                password=User.objects.make_random_password()  # Random password
            )
            
            # Now create Colleague linked to this User
            colleague = Colleague.objects.create(
                user=user,  # Link to the User we just created
                staff_id=last_name[:20].upper(),  # Use last name as temp staff_id
                title='Dr',  # Default title
                fte=1.0,  # Default full-time
                contract_type='permanent',  # Adjust if needed
                employment_status='current'
            )
            
            return colleague
            
        except Exception as e:
            print(f"Error creating colleague for {author_name}: {str(e)}")
            return None
    
    return None


def map_publication_type_to_code(type_string):
    """
    Map CSV type values to your model's single-letter codes
    Your choices: A=Article, B=Book, C=Chapter, D=Conference, E=Patent, F=Software, G=Performance, H=Other
    """
    type_map = {
        'Article': 'A',
        'Book': 'B',
        'Chapter': 'C',
        'Conference': 'D',
        'Comment/debate': 'A',  # Treat as Article
        'Review': 'A',  # Treat as Article
        'Patent': 'E',
        'Software': 'F',
        'Performance': 'G',
        'Exhibition': 'G',
    }
    return type_map.get(type_string, 'H')  # Default to 'H' (Other)


def safe_parse_date(date_string):
    """
    Parse various date formats safely
    Returns a date object or today's date if parsing fails
    """
    if not date_string or not isinstance(date_string, str):
        return date.today()  # Return today as default since field is required
    
    try:
        # Try full datetime first
        if ' ' in date_string:
            result = parse_datetime(date_string)
            if result:
                return result.date()
        # Try just date
        parsed = django_parse_date(date_string)
        if parsed:
            return parsed
    except:
        pass
    
    return date.today()  # Return today as default since field is required


def extract_first_author_name(person_string):
    """
    Extract the first author's name in a cleaner format
    """
    authors = parse_authors(person_string)
    if authors:
        return authors[0]
    return "Unknown"




@login_required
def import_outputs(request):
    """
    View for importing outputs from CSV file
    """
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            skip_duplicates = form.cleaned_data['skip_duplicates']
            create_missing_staff = form.cleaned_data['create_missing_staff']
            
            # Read CSV file
            csv_file.seek(0)
            content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            
            # Statistics
            stats = {
                'total': 0,
                'created': 0,
                'skipped': 0,
                'errors': 0,
                'error_details': []
            }
            
            # Process each row - use savepoint per row for better error handling
            for row_num, row in enumerate(csv_reader, start=2):
                stats['total'] += 1
                
                try:
                    # Use a savepoint for each row so one error doesn't break everything
                    with transaction.atomic():
                        # Extract basic info
                        title = row.get('Title', '').strip()
                        if not title:
                            stats['skipped'] += 1
                            stats['error_details'].append(f'Row {row_num}: Missing title')
                            continue
                        
                        # Check for duplicates
                        if skip_duplicates and Output.objects.filter(title=title).exists():
                            stats['skipped'] += 1
                            continue
                        
                        # Parse authors
                        person_string = row.get('Person', '')
                        authors = parse_authors(person_string)
                        
                        if not authors:
                            stats['skipped'] += 1
                            stats['error_details'].append(f'Row {row_num}: No authors found')
                            continue
                        
                        # Get or create primary author (first author)
                        primary_colleague = find_or_create_colleague(authors[0], create_missing_staff, set_as_coauthor=True )


                        if not primary_colleague:
                            stats['skipped'] += 1
                            stats['error_details'].append(
                                f'Row {row_num}: Could not find/create colleague "{authors[0]}"'
                            )
                            continue
                        
                        # Map publication type to single-letter code
                        pub_type_code = map_publication_type_to_code(row.get('Type', ''))
                        
                        # Parse dates
                        publication_date = safe_parse_date(
                            row.get('Full date') or row.get('Earliest published date')
                        )
                        
                        # Extract publication venue (journal + publisher)
                        journal = row.get('Journal title', '') or ''
                        publisher = row.get('Publisher', '') or ''
                        
                        if journal and publisher:
                            venue = f"{journal} ({publisher})"
                        elif journal:
                            venue = journal
                        elif publisher:
                            venue = publisher
                        else:
                            venue = 'Unknown'  # Required field, must have value
                        
                        # Extract DOI and build URL if no URL provided
                        doi = (row.get('DOIs (Digital Object Identifiers)', '') or '').strip()
                        if doi:
                            # Clean DOI - may have multiple DOIs, take first one
                            doi_clean = doi.split(',')[0].strip()
                            # Remove any existing DOI URL prefix
                            doi_clean = doi_clean.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
                            doi = doi_clean[:200]  # Truncate to field length
                            url = f"https://doi.org/{doi}"
                        else:
                            doi = ''
                            url = ''
                        
                        # Check Open Access status
                        oa_status = row.get('REF Open Access compliance status', '')
                        is_open_access = oa_status.startswith('REF OA Compliance MET')
                        
                        # Build internal notes with all the import metadata
                        internal_notes = (
                            f"Imported from CSV on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                            f"Pure ID: {row.get('Pure ID', 'N/A')}\n"
                            f"Organisational unit: {row.get('Organisational unit', 'N/A')}\n"
                            f"Managing org unit: {row.get('Managing organisational unit', 'N/A')}\n"
                            f"Number of internal persons: {row.get('Number of internal persons', 'N/A')}\n"
                            f"Publisher: {publisher}\n"
                            f"Journal: {journal}\n"
                            f"OA Status: {oa_status}\n"
                            f"OA Notes: {row.get('Open Access compliance notes', 'N/A')}\n"
                            f"Original CSV Status: {row.get('Current publication status', 'N/A')}\n"
                        )
                        
                        # Create output with ALL required fields
                        output = Output.objects.create(
                            # Required ForeignKey
                            colleague=primary_colleague,
                            
                            # Basic publication info (all required)
                            title=title[:500],  # Truncate to max_length
                            publication_type=pub_type_code,  # Single letter code
                            publication_date=publication_date,
                            publication_venue=venue[:300],  # Truncate to max_length
                            
                            # Volume/issue/pages (required, use empty string if missing)
                            volume=(row.get('Host publication volume', '') or '')[:50],
                            issue=(row.get('Issue number', '') or '')[:50],
                            pages=(row.get('Pages (from-to)', '') or '')[:50],
                            
                            # Identifiers (required, use empty string if missing)
                            doi=doi,
                            isbn=(row.get('ISBN (print)', '') or '')[:50],
                            url=url[:500] if url else '',
                            
                            # Author info (required)
                            all_authors=person_string if person_string else extract_first_author_name(person_string),
                            author_position=1,  # Default to first author
                            
                            # REF-specific fields (required, use defaults)
                            uoa='Main Panel A',  # Default - adjust as needed
                            status='draft',  # Default status for imported items
                            quality_rating='U',  # Unclassified until reviewed
                            
                            # Boolean flags (required)
                            is_double_weighted=False,  # Default
                            is_interdisciplinary=False,  # Default
                            is_open_access=is_open_access,
                            
                            # Text fields (required, use default if empty)
                            abstract=row.get('Abstract', '') or 'Abstract not provided.',
                            keywords=row.get('Keywords', '') or 'Not specified',
                            internal_notes=internal_notes,
                        )
                        
                        stats['created'] += 1
                        
                except Exception as e:
                    stats['errors'] += 1
                    error_msg = f'Row {row_num}: {str(e)}'
                    stats['error_details'].append(error_msg)
                    # Print to console for debugging
                    print(f"Import error: {error_msg}")
            
            # Display results
            messages.success(
                request,
                f"Import completed! Created: {stats['created']}, "
                f"Skipped: {stats['skipped']}, Errors: {stats['errors']}"
            )
            
            if stats['error_details']:
                for error in stats['error_details'][:10]:  # Show first 10 errors
                    messages.warning(request, error)
                
                if len(stats['error_details']) > 10:
                    messages.warning(
                        request,
                        f"...and {len(stats['error_details']) - 10} more errors"
                    )
            
            return redirect('output_list')
    
    else:
        form = CSVUploadForm()
    
    return render(request, 'core/import_outputs.html', {
        'form': form,
        'title': 'Import Outputs from CSV'
    })
"""
COLLEAGUE MERGE FUNCTIONALITY

Add these functions to core/views.py
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count
from core.models import Colleague, Output

# Helper function to check if user is admin/staff
def is_staff_user(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_user)
def find_duplicate_colleagues(request):
    """
    Find potential duplicate colleagues based on similar names
    """
    # Find colleagues with similar last names
    from collections import defaultdict
    
    all_colleagues = Colleague.objects.select_related('user').all()
    
    # Group by similar last names (case insensitive)
    name_groups = defaultdict(list)
    for colleague in all_colleagues:
        if colleague.user:
            last_name_key = colleague.user.last_name.lower().strip()
            name_groups[last_name_key].append(colleague)
    
    # Find groups with more than one colleague
    duplicates = []
    for last_name, colleagues_list in name_groups.items():
        if len(colleagues_list) > 1:
            # Add details about each group
            duplicates.append({
                'last_name': last_name,
                'colleagues': colleagues_list,
                'count': len(colleagues_list)
            })
    
    # Sort by number of duplicates
    duplicates.sort(key=lambda x: x['count'], reverse=True)
    
    return render(request, 'core/duplicate_colleagues.html', {
        'duplicates': duplicates,
        'title': 'Find Duplicate Colleagues'
    })


@login_required
@user_passes_test(is_staff_user)
def merge_colleagues(request):
    """
    Merge two or more colleagues into one
    """
    if request.method == 'POST':
        # Get the IDs of colleagues to merge
        colleague_ids = request.POST.getlist('colleague_ids')
        primary_id = request.POST.get('primary_id')
        
        if len(colleague_ids) < 2:
            messages.error(request, 'Please select at least 2 colleagues to merge')
            return redirect('find_duplicate_colleagues')
        
        if not primary_id or primary_id not in colleague_ids:
            messages.error(request, 'Please select a primary colleague to keep')
            return redirect('find_duplicate_colleagues')
        
        try:
            with transaction.atomic():
                # Get the primary colleague (the one to keep)
                primary = get_object_or_404(Colleague, id=primary_id)
                
                # Get all colleagues to merge
                colleagues_to_merge = Colleague.objects.filter(
                    id__in=colleague_ids
                ).exclude(id=primary_id)
                
                merge_count = 0
                outputs_moved = 0
                
                for colleague in colleagues_to_merge:
                    # Move all outputs to the primary colleague
                    outputs = Output.objects.filter(colleague=colleague)
                    outputs_count = outputs.count()
                    outputs.update(colleague=primary)
                    outputs_moved += outputs_count
                    
                    # Move internal reviews if any
                    from core.models import InternalReview
                    InternalReview.objects.filter(reviewer=colleague).update(reviewer=primary)
                    
                    # Move internal panel memberships if any
                    from core.models import InternalPanelMember
                    InternalPanelMember.objects.filter(colleague=colleague).update(colleague=primary)
                    
                    # Keep a record of the merge in notes
                    merge_note = (
                        f"\n\nMerged from: {colleague.user.get_full_name() if colleague.user else 'Unknown'} "
                        f"(Staff ID: {colleague.staff_id}) "
                        f"on {datetime.now().strftime('%Y-%m-%d')}"
                    )
                    
                    # Delete the duplicate colleague
                    # Note: This will also delete their User account
                    duplicate_user = colleague.user
                    colleague.delete()
                    if duplicate_user:
                        duplicate_user.delete()
                    
                    merge_count += 1
                
                messages.success(
                    request,
                    f'Successfully merged {merge_count} colleague(s) into '
                    f'{primary.user.get_full_name() if primary.user else primary.staff_id}. '
                    f'Moved {outputs_moved} output(s).'
                )
                
        except Exception as e:
            messages.error(request, f'Error merging colleagues: {str(e)}')
        
        return redirect('colleague_list')
    
    # GET request - show merge form
    colleague_ids = request.GET.getlist('ids')
    
    if not colleague_ids:
        messages.warning(request, 'No colleagues selected for merging')
        return redirect('find_duplicate_colleagues')
    
    colleagues = Colleague.objects.filter(id__in=colleague_ids).select_related('user')
    
    # Get output counts for each colleague
    for colleague in colleagues:
        colleague.output_count = Output.objects.filter(colleague=colleague).count()
    
    return render(request, 'core/merge_colleagues.html', {
        'colleagues': colleagues,
        'title': 'Merge Colleagues'
    })



@login_required
@user_passes_test(is_staff_user)
def update_colleague_category(request, colleague_id):
    """
    Update a colleague's category
    """
    if request.method == 'POST':
        colleague = get_object_or_404(Colleague, id=colleague_id)
        new_category = request.POST.get('category')
        
        if new_category in ['employee', 'former', 'coauthor', 'non_independent']:
            colleague.colleague_category = new_category
            colleague.save()
            
            messages.success(
                request,
                f'Updated category for {colleague.user.get_full_name() if colleague.user else colleague.staff_id}'
            )
        else:
            messages.error(request, 'Invalid category')
    
    return redirect(request.META.get('HTTP_REFERER', 'colleague_list'))
"""
COLLEAGUE MERGE FUNCTIONALITY

Add these functions to core/views.py
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count
from core.models import Colleague, Output

# Helper function to check if user is admin/staff
def is_staff_user(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_user)
def find_duplicate_colleagues(request):
    """
    Find potential duplicate colleagues based on similar names
    """
    # Find colleagues with similar last names
    from collections import defaultdict
    
    all_colleagues = Colleague.objects.select_related('user').all()
    
    # Group by similar last names (case insensitive)
    name_groups = defaultdict(list)
    for colleague in all_colleagues:
        if colleague.user:
            last_name_key = colleague.user.last_name.lower().strip()
            name_groups[last_name_key].append(colleague)
    
    # Find groups with more than one colleague
    duplicates = []
    for last_name, colleagues_list in name_groups.items():
        if len(colleagues_list) > 1:
            # Add details about each group
            duplicates.append({
                'last_name': last_name,
                'colleagues': colleagues_list,
                'count': len(colleagues_list)
            })
    
    # Sort by number of duplicates
    duplicates.sort(key=lambda x: x['count'], reverse=True)
    
    return render(request, 'core/duplicate_colleagues.html', {
        'duplicates': duplicates,
        'title': 'Find Duplicate Colleagues'
    })


@login_required
@user_passes_test(is_staff_user)
def merge_colleagues(request):
    """
    Merge two or more colleagues into one
    """
    if request.method == 'POST':
        # Get the IDs of colleagues to merge
        colleague_ids = request.POST.getlist('colleague_ids')
        primary_id = request.POST.get('primary_id')
        
        if len(colleague_ids) < 2:
            messages.error(request, 'Please select at least 2 colleagues to merge')
            return redirect('find_duplicate_colleagues')
        
        if not primary_id or primary_id not in colleague_ids:
            messages.error(request, 'Please select a primary colleague to keep')
            return redirect('find_duplicate_colleagues')
        
        try:
            with transaction.atomic():
                # Get the primary colleague (the one to keep)
                primary = get_object_or_404(Colleague, id=primary_id)
                
                # Get all colleagues to merge
                colleagues_to_merge = Colleague.objects.filter(
                    id__in=colleague_ids
                ).exclude(id=primary_id)
                
                merge_count = 0
                outputs_moved = 0
                
                for colleague in colleagues_to_merge:
                    # Move all outputs to the primary colleague
                    outputs = Output.objects.filter(colleague=colleague)
                    outputs_count = outputs.count()
                    outputs.update(colleague=primary)
                    outputs_moved += outputs_count
                    
                    # Move internal reviews if any
                    from core.models import InternalReview
                    InternalReview.objects.filter(reviewer=colleague).update(reviewer=primary)
                    
                    # Move internal panel memberships if any
                    from core.models import InternalPanelMember
                    InternalPanelMember.objects.filter(colleague=colleague).update(colleague=primary)
                    
                    # Keep a record of the merge in notes
                    merge_note = (
                        f"\n\nMerged from: {colleague.user.get_full_name() if colleague.user else 'Unknown'} "
                        f"(Staff ID: {colleague.staff_id}) "
                        f"on {datetime.now().strftime('%Y-%m-%d')}"
                    )
                    
                    # Delete the duplicate colleague
                    # Note: This will also delete their User account
                    duplicate_user = colleague.user
                    colleague.delete()
                    if duplicate_user:
                        duplicate_user.delete()
                    
                    merge_count += 1
                
                messages.success(
                    request,
                    f'Successfully merged {merge_count} colleague(s) into '
                    f'{primary.user.get_full_name() if primary.user else primary.staff_id}. '
                    f'Moved {outputs_moved} output(s).'
                )
                
        except Exception as e:
            messages.error(request, f'Error merging colleagues: {str(e)}')
        
        return redirect('colleague_list')
    
    # GET request - show merge form
    colleague_ids = request.GET.getlist('ids')
    
    if not colleague_ids:
        messages.warning(request, 'No colleagues selected for merging')
        return redirect('find_duplicate_colleagues')
    
    colleagues = Colleague.objects.filter(id__in=colleague_ids).select_related('user')
    
    # Get output counts for each colleague
    for colleague in colleagues:
        colleague.output_count = Output.objects.filter(colleague=colleague).count()
    
    return render(request, 'core/merge_colleagues.html', {
        'colleagues': colleagues,
        'title': 'Merge Colleagues'
    })


@login_required
def colleague_list(request):
    """
    List all colleagues with filtering by category
    """
    # Get filter from query params
    category_filter = request.GET.get('category', 'all')
    
    # Base queryset
    colleagues = Colleague.objects.select_related('user').annotate(
        output_count=Count('outputs')
    )
    
    # Apply filters
    if category_filter != 'all':
        colleagues = colleagues.filter(colleague_category=category_filter)
    
    # Order by name
    colleagues = colleagues.order_by('user__last_name', 'user__first_name')
    
    # Get category counts for sidebar
    category_counts = {
        'all': Colleague.objects.count(),
        'independent': Colleague.objects.filter(colleague_category='independent').count(),
        'non_independent': Colleague.objects.filter(colleague_category='non_independent').count(),  # UNDERSCORE!
        'postdoc': Colleague.objects.filter(colleague_category='postdoc').count(),
        'research_assistant': Colleague.objects.filter(colleague_category='research_assistant').count(),
        'academic': Colleague.objects.filter(colleague_category='academic').count(),
        'support': Colleague.objects.filter(colleague_category='support').count(),
        'employee': Colleague.objects.filter(colleague_category='employee').count(),
        'former': Colleague.objects.filter(colleague_category='former').count(),
        'coauthor': Colleague.objects.filter(colleague_category='coauthor').count(),
    }
    
    # Add employment status counts
    employment_counts = {
        'current': Colleague.objects.filter(employment_status='current').count(),
        'former': Colleague.objects.filter(employment_status='former').count(),
    }
    
    context = {
        'colleagues': colleagues,
        'category_counts': category_counts,
        'employment_counts': employment_counts,
        'current_filter': category_filter,
    }
    
    return render(request, 'core/colleague_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def update_colleague_category(request, colleague_id):
    """
    Update a colleague's category
    """
    if request.method == 'POST':
        colleague = get_object_or_404(Colleague, id=colleague_id)
        new_category = request.POST.get('category')
        
        if new_category in ['employee', 'former', 'coauthor', 'non_independent']:
            colleague.colleague_category = new_category
            colleague.save()
            
            messages.success(
                request,
                f'Updated category for {colleague.user.get_full_name() if colleague.user else colleague.staff_id}'
            )
        else:
            messages.error(request, 'Invalid category')
    
    return redirect(request.META.get('HTTP_REFERER', 'colleague_list'))

@login_required
@user_passes_test(is_admin)
def internal_panel_assignment_delete(request, pk):
    """Delete an internal panel assignment"""
    assignment = get_object_or_404(InternalPanelAssignment, pk=pk)
    output_pk = assignment.output.pk
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Internal panel assignment deleted successfully.')
        return redirect('output_detail', pk=output_pk)
    
    return render(request, 'core/internal_panel_assignment_confirm_delete.html', {
        'assignment': assignment
    })


@login_required
@user_passes_test(is_admin)
def critical_friend_assignment_delete(request, pk):
    """Delete a critical friend assignment"""
    assignment = get_object_or_404(CriticalFriendAssignment, pk=pk)
    output_pk = assignment.output.pk
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Critical friend assignment deleted successfully.')
        return redirect('output_detail', pk=output_pk)
    
    return render(request, 'core/critical_friend_assignment_confirm_delete.html', {
        'assignment': assignment
    })

