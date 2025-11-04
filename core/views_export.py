# ============================================================
# REF MANAGER - EXPORT WITH BOTH INTERNAL PANEL & CRITICAL FRIENDS
# FIXED: colleague.user path for accessing User fields
# ============================================================

# FILE: core/views_export.py (UPDATED VERSION)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from .models import (
    CriticalFriendAssignment, 
    InternalPanelAssignment,
    Output, 
    CriticalFriend, 
    InternalPanelMember
)
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO
import csv
from datetime import datetime

@login_required
def export_assignments_view(request):
    """
    View to display export options and filters
    Shows both internal panel members and critical friends
    """
    # Get both types of reviewers
    critical_friends = CriticalFriend.objects.all().order_by('name')
    # InternalPanelMember → colleague (Colleague model) → user (User model)
    internal_panel = InternalPanelMember.objects.select_related('colleague__user').filter(
        is_active=True
    ).order_by('colleague__user__last_name', 'colleague__user__first_name')
    
    # Get all unique authors (colleagues) from outputs
    colleague_ids = Output.objects.values_list('colleague', flat=True).distinct()
    authors = User.objects.filter(id__in=colleague_ids).order_by('last_name', 'first_name')
    
    if not authors.exists():
        authors = User.objects.filter(is_staff=True).order_by('last_name', 'first_name')
    
    context = {
        'critical_friends': critical_friends,
        'internal_panel': internal_panel,
        'staff_members': authors,
    }
    
    return render(request, 'core/export_assignments.html', context)


@login_required
def export_assignments_excel(request):
    """
    Export review assignments to Excel with clickable links
    Includes BOTH internal panel and critical friend assignments
    """
    # Get filter parameters
    reviewer_id = request.GET.get('reviewer')
    author_id = request.GET.get('author')
    status = request.GET.get('status')
    recipient_type = request.GET.get('recipient_type', 'all')
    
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Review Assignments"
    
    # Define styles
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=12)
    internal_fill = PatternFill(start_color="E8F4F8", end_color="E8F4F8", fill_type="solid")  # Light blue for internal
    external_fill = PatternFill(start_color="FFF8E1", end_color="FFF8E1", fill_type="solid")  # Light yellow for external
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Headers
    headers = [
        'Reviewer Type',
        'Reviewer Name',
        'Reviewer Email',
        'Output Title',
        'Author',
        'Quality Rating',
        'Status',
        'Due Date',
        'Priority',
        'Link to Paper',
        'Notes/Instructions'
    ]
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    row_num = 2
    
    # PART 1: Get Internal Panel Assignments
    if recipient_type in ['all', 'internal']:
        internal_assignments = InternalPanelAssignment.objects.select_related(
            'output', 'panel_member__colleague__user', 'output__colleague__user'
        ).all()
        
        # Apply filters
        if reviewer_id:
            internal_assignments = internal_assignments.filter(panel_member_id=reviewer_id)
        if author_id:
            internal_assignments = internal_assignments.filter(output__colleague_id=author_id)
        if status:
            internal_assignments = internal_assignments.filter(status=status)
        
        # Add internal panel assignments to Excel
        for assignment in internal_assignments:
            output = assignment.output
            panel_member = assignment.panel_member
            
            # InternalPanelMember → colleague → user (User model with name/email)
            if panel_member.colleague and panel_member.colleague.user:
                reviewer_name = panel_member.colleague.user.get_full_name()
                reviewer_email = panel_member.colleague.user.email
            else:
                reviewer_name = 'Unknown'
                reviewer_email = 'No email'
            
            # Get author name - Output.colleague is also Colleague model → user
            if hasattr(output, 'colleague') and output.colleague and output.colleague.user:
                author_name = output.colleague.user.get_full_name()
            elif hasattr(output, 'all_authors') and output.all_authors:
                author_name = output.all_authors
            else:
                author_name = 'Unknown'
            
            # Get priority
            try:
                priority = assignment.get_priority_display()
            except:
                priority = 'Normal'
            
            # Prepare data
            data = [
                'Internal Panel',  # Reviewer Type
                reviewer_name,
                reviewer_email,
                output.title,
                author_name,
                output.get_quality_rating_display() if output.quality_rating else 'Not Rated',
                assignment.get_status_display(),
                assignment.due_date.strftime('%Y-%m-%d') if hasattr(assignment, 'due_date') and assignment.due_date else 'No deadline',
                priority,
                output.pdf_file.url if output.pdf_file else 'No file',
                assignment.notes if hasattr(assignment, 'notes') else ''
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = value
                cell.border = border
                cell.alignment = Alignment(vertical='top', wrap_text=True)
                
                # Color code internal panel rows
                if col_num > 1:  # Skip the "Type" column
                    cell.fill = internal_fill
                
                # Make link clickable
                if col_num == 10 and output.pdf_file:
                    full_url = request.build_absolute_uri(output.pdf_file.url)
                    cell.hyperlink = full_url
                    cell.font = Font(color="0563C1", underline="single")
            
            row_num += 1
    
    # PART 2: Get Critical Friend Assignments
    if recipient_type in ['all', 'critical_friends']:
        cf_assignments = CriticalFriendAssignment.objects.select_related(
            'output', 'critical_friend', 'output__colleague__user'
        ).all()
        
        # Apply filters
        if reviewer_id:
            cf_assignments = cf_assignments.filter(critical_friend_id=reviewer_id)
        if author_id:
            cf_assignments = cf_assignments.filter(output__colleague_id=author_id)
        if status:
            cf_assignments = cf_assignments.filter(status=status)
        
        # Add critical friend assignments to Excel
        for assignment in cf_assignments:
            output = assignment.output
            reviewer = assignment.critical_friend
            
            # Get author name - Output.colleague is Colleague model → user
            if hasattr(output, 'colleague') and output.colleague and output.colleague.user:
                author_name = output.colleague.user.get_full_name()
            elif hasattr(output, 'all_authors') and output.all_authors:
                author_name = output.all_authors
            else:
                author_name = 'Unknown'
            
            # Get priority
            try:
                priority = assignment.get_priority_display()
            except:
                priority = 'Normal'
            
            # Prepare data
            data = [
                'Critical Friend',  # Reviewer Type
                reviewer.name,
                reviewer.email,
                output.title,
                author_name,
                output.get_quality_rating_display() if output.quality_rating else 'Not Rated',
                assignment.get_status_display(),
                assignment.due_date.strftime('%Y-%m-%d') if assignment.due_date else 'No deadline',
                priority,
                output.pdf_file.url if output.pdf_file else 'No file',
                assignment.notes or ''
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = value
                cell.border = border
                cell.alignment = Alignment(vertical='top', wrap_text=True)
                
                # Color code critical friend rows
                if col_num > 1:  # Skip the "Type" column
                    cell.fill = external_fill
                
                # Make link clickable
                if col_num == 10 and output.pdf_file:
                    full_url = request.build_absolute_uri(output.pdf_file.url)
                    cell.hyperlink = full_url
                    cell.font = Font(color="0563C1", underline="single")
            
            row_num += 1
    
    # Adjust column widths
    column_widths = {
        'A': 18,  # Reviewer Type
        'B': 20,  # Reviewer Name
        'C': 25,  # Email
        'D': 40,  # Title
        'E': 20,  # Author
        'F': 15,  # Quality
        'G': 15,  # Status
        'H': 12,  # Due Date
        'I': 12,  # Priority
        'J': 15,  # Link
        'K': 30,  # Notes
    }
    
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    
    # Freeze header row
    ws.freeze_panes = 'A2'
    
    # Create response
    output_buffer = BytesIO()
    wb.save(output_buffer)
    output_buffer.seek(0)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'review_assignments_{timestamp}.xlsx'
    
    response = HttpResponse(
        output_buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def export_assignments_csv(request):
    """
    Export review assignments to CSV (alternative format)
    Includes BOTH internal panel and critical friend assignments
    """
    # Get filter parameters
    reviewer_id = request.GET.get('reviewer')
    author_id = request.GET.get('author')
    status = request.GET.get('status')
    recipient_type = request.GET.get('recipient_type', 'all')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="review_assignments_{timestamp}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow([
        'Reviewer Type',
        'Reviewer Name',
        'Reviewer Email',
        'Output Title',
        'Author',
        'Quality Rating',
        'Status',
        'Due Date',
        'Link to Paper',
        'Notes/Instructions'
    ])
    
    # PART 1: Internal Panel Assignments
    if recipient_type in ['all', 'internal']:
        internal_assignments = InternalPanelAssignment.objects.select_related(
            'output', 'panel_member__colleague__user', 'output__colleague__user'
        ).all()
        
        if reviewer_id:
            internal_assignments = internal_assignments.filter(panel_member_id=reviewer_id)
        if author_id:
            internal_assignments = internal_assignments.filter(output__colleague_id=author_id)
        if status:
            internal_assignments = internal_assignments.filter(status=status)
        
        for assignment in internal_assignments:
            output = assignment.output
            panel_member = assignment.panel_member
            
            # InternalPanelMember → colleague → user (User model with name/email)
            if panel_member.colleague and panel_member.colleague.user:
                reviewer_name = panel_member.colleague.user.get_full_name()
                reviewer_email = panel_member.colleague.user.email
            else:
                reviewer_name = 'Unknown'
                reviewer_email = 'No email'
            
            # Get author name - Output.colleague is Colleague model → user
            if hasattr(output, 'colleague') and output.colleague and output.colleague.user:
                author_name = output.colleague.user.get_full_name()
            elif hasattr(output, 'all_authors') and output.all_authors:
                author_name = output.all_authors
            else:
                author_name = 'Unknown'
            
            writer.writerow([
                'Internal Panel',
                reviewer_name,
                reviewer_email,
                output.title,
                author_name,
                output.get_quality_rating_display() if output.quality_rating else 'Not Rated',
                assignment.get_status_display(),
                assignment.due_date.strftime('%Y-%m-%d') if hasattr(assignment, 'due_date') and assignment.due_date else 'No deadline',
                request.build_absolute_uri(output.pdf_file.url) if output.pdf_file else 'No file',
                assignment.notes if hasattr(assignment, 'notes') else ''
            ])
    
    # PART 2: Critical Friend Assignments
    if recipient_type in ['all', 'critical_friends']:
        cf_assignments = CriticalFriendAssignment.objects.select_related(
            'output', 'critical_friend', 'output__colleague__user'
        ).all()
        
        if reviewer_id:
            cf_assignments = cf_assignments.filter(critical_friend_id=reviewer_id)
        if author_id:
            cf_assignments = cf_assignments.filter(output__colleague_id=author_id)
        if status:
            cf_assignments = cf_assignments.filter(status=status)
        
        for assignment in cf_assignments:
            output = assignment.output
            reviewer = assignment.critical_friend
            
            # Get author name - Output.colleague is Colleague model → user
            if hasattr(output, 'colleague') and output.colleague and output.colleague.user:
                author_name = output.colleague.user.get_full_name()
            elif hasattr(output, 'all_authors') and output.all_authors:
                author_name = output.all_authors
            else:
                author_name = 'Unknown'
            
            writer.writerow([
                'Critical Friend',
                reviewer.name,
                reviewer.email,
                output.title,
                author_name,
                output.get_quality_rating_display() if output.quality_rating else 'Not Rated',
                assignment.get_status_display(),
                assignment.due_date.strftime('%Y-%m-%d') if assignment.due_date else 'No deadline',
                request.build_absolute_uri(output.pdf_file.url) if output.pdf_file else 'No file',
                assignment.notes or ''
            ])
    
    return response
