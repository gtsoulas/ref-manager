from django.contrib import admin
from .models import Task
from .models import (
    Colleague, Output, CriticalFriend, CriticalFriendAssignment,
    Request, InternalReview, InternalPanelMember, InternalPanelAssignment
)

@admin.register(Colleague)
class ColleagueAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'staff_id', 
        'colleague_category',  # Make sure this is here
        'employment_status',
        'unit_of_assessment'
    ]
    list_filter = [
        'colleague_category',  # Add filter by category
        'employment_status',
        'unit_of_assessment',
        'is_returnable'
    ]
    search_fields = [
        'user__first_name',
        'user__last_name',
        'staff_id'
    ]

    search_fields = ['user__first_name', 'user__last_name', 'staff_id']
    readonly_fields = ['created_at', 'updated_at']
    
    # Optional: Add fieldsets for better organization
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('staff_id', 'title')
        }),
        ('Employment Information', {
            'fields': (
                'fte', 
                'contract_type', 
                'employment_status',      # NEW FIELD
                'employment_end_date'     # NEW FIELD
            )
        }),
        ('REF Information', {
            'fields': ('unit_of_assessment', 'is_returnable', 'submission_group')
        }),
        ('Contact Information', {
            'fields': ('office', 'phone')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Output)
class OutputAdmin(admin.ModelAdmin):
    list_display = ['title', 'colleague', 'publication_type', 'publication_date', 'status', 'quality_rating']
    list_filter = ['status', 'quality_rating', 'publication_type', 'uoa']
    search_fields = ['title', 'all_authors', 'doi']
    date_hierarchy = 'publication_date'
    readonly_fields = ['created_at', 'updated_at', 'submitted_date', 'approved_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('colleague', 'title', 'publication_type', 'publication_date')
        }),
        ('Publication Details', {
            'fields': ('publication_venue', 'volume', 'issue', 'pages', 'doi', 'isbn', 'url')
        }),
        ('Authors', {
            'fields': ('all_authors', 'author_position')
        }),
        ('REF Details', {
            'fields': ('uoa', 'status', 'quality_rating', 'is_double_weighted', 
                      'is_interdisciplinary', 'is_open_access')
        }),
        ('Files', {
            'fields': ('pdf_file', 'supplementary_file')
        }),
        ('Additional Information', {
            'fields': ('abstract', 'keywords', 'internal_notes')
        }),
        ('Timestamps', {
            'fields': ('submitted_date', 'approved_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CriticalFriend)
class CriticalFriendAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'is_internal', 'availability', 'current_workload', 'max_assignments']
    list_filter = ['is_internal', 'availability', 'institution']
    search_fields = ['name', 'email', 'institution', 'expertise_areas']
    list_editable = ['is_internal']  # Add this so you can quickly mark internal reviewers
    readonly_fields = ['created_at', 'updated_at']  # Changed from 'added_date', 'last_contacted'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'institution', 'department', 'is_internal')
        }),
        ('Contact & Identity', {
            'fields': ('phone', 'orcid', 'user_account')
        }),
        ('Expertise & Availability', {
            'fields': ('expertise_areas', 'research_interests', 'availability', 'max_assignments')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def current_workload(self, obj):
        return f"{obj.current_workload}/{obj.max_assignments}"
    current_workload.short_description = 'Workload'
    
@admin.register(CriticalFriendAssignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['output', 'critical_friend', 'status', 'assigned_date', 'due_date', 'quality_assessment']
    list_filter = ['status', 'quality_assessment']
    search_fields = ['output__title', 'critical_friend__name']
    date_hierarchy = 'assigned_date'
    readonly_fields = ['assigned_date', 'accepted_date', 'completed_date']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['subject', 'from_entity', 'deadline', 'priority', 'status', 'assigned_to']
    list_filter = ['status', 'priority']
    search_fields = ['subject', 'from_entity', 'description']
    date_hierarchy = 'deadline'
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(InternalReview)
class InternalReviewAdmin(admin.ModelAdmin):
    list_display = ['output', 'reviewer', 'quality_assessment', 'reviewed_date']
    list_filter = ['quality_assessment']
    search_fields = ['output__title', 'reviewer__username']
    date_hierarchy = 'reviewed_date'

@admin.register(InternalPanelMember)
class InternalPanelMemberAdmin(admin.ModelAdmin):
    list_display = ['colleague', 'role', 'expertise_area', 'is_active', 'appointed_date']
    list_filter = ['role', 'is_active', 'appointed_date']
    search_fields = ['colleague__user__first_name', 'colleague__user__last_name', 'expertise_area']
    date_hierarchy = 'appointed_date'


@admin.register(InternalPanelAssignment)
class InternalPanelAssignmentAdmin(admin.ModelAdmin):
    list_display = ['output', 'panel_member', 'status', 'assigned_date', 'review_date']
    list_filter = ['status', 'assigned_date', 'review_date']
    search_fields = ['output__title', 'panel_member__colleague__user__last_name']
    date_hierarchy = 'assigned_date'



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'priority',
        'status',
        'assigned_to',
        'due_date',
        'is_overdue',
        'created_at'
    ]
    list_filter = ['status', 'priority', 'category', 'assigned_to']
    search_fields = ['title', 'description', 'notes']
    date_hierarchy = 'due_date'
    ordering = ['-priority', 'due_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Dates', {
            'fields': ('start_date', 'due_date', 'completed_date')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_by', 'completed_date']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


