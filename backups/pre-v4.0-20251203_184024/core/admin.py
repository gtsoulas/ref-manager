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
        'colleague_category',
        'employment_status',
        'unit_of_assessment'
    ]
    list_filter = [
        'colleague_category',
        'employment_status',
        'unit_of_assessment',
        'is_returnable'
    ]
    search_fields = [
        'user__first_name',
        'user__last_name',
        'staff_id'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
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
                'employment_status',
                'employment_end_date'
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
    list_display = ['title', 'colleague', 'publication_type', 'publication_year', 'status', 'quality_rating']
    list_filter = ['status', 'quality_rating', 'publication_type', 'uoa']
    search_fields = ['title', 'all_authors', 'doi']
    readonly_fields = ['created_at', 'updated_at', 'submitted_date', 'approved_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('colleague', 'title', 'publication_type', 'publication_year')
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
    # FIXED: Removed 'is_internal' - field doesn't exist in model
    list_display = ['name', 'institution', 'availability', 'current_workload', 'max_assignments']
    list_filter = ['availability', 'institution']
    search_fields = ['name', 'email', 'institution', 'expertise_areas']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'institution', 'department')
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
    # FIXED: Removed 'accepted_date' - field doesn't exist, only assigned_date and completed_date
    readonly_fields = ['assigned_date', 'completed_date']


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['subject', 'from_entity', 'deadline', 'priority', 'status', 'assigned_to']
    list_filter = ['status', 'priority']
    search_fields = ['subject', 'from_entity', 'description']
    date_hierarchy = 'deadline'
    # FIXED: Changed 'completed_at' to 'completed_date'
    readonly_fields = ['created_at', 'updated_at', 'completed_date']


@admin.register(InternalReview)
class InternalReviewAdmin(admin.ModelAdmin):
    # FIXED: Changed 'reviewed_date' to 'created_at'
    list_display = ['output', 'reviewer', 'quality_assessment', 'created_at']
    list_filter = ['quality_assessment']
    search_fields = ['output__title', 'reviewer__username']
    date_hierarchy = 'created_at'


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
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Risk Assessment Framework Admin
from .models import REFSubmission, SubmissionOutput

@admin.register(REFSubmission)
class REFSubmissionAdmin(admin.ModelAdmin):
    # FIXED: Removed 'is_active', 'is_final' - fields don't exist in model
    list_display = [
        'name', 'uoa', 'submission_year', 'status',
        'portfolio_quality_score', 'portfolio_risk_score'
    ]
    list_filter = ['status', 'submission_year']
    search_fields = ['name', 'uoa', 'description']
    # FIXED: Removed non-existent fields from readonly_fields
    readonly_fields = [
        'portfolio_quality_score', 'portfolio_risk_score',
        'representativeness_score', 'equality_score', 'gender_balance_score',
        'metrics_last_calculated'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'uoa', 'submission_year', 'description')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Optimization Weights', {
            'fields': (
                'weight_quality', 'weight_risk', 'weight_representativeness',
                'weight_equality', 'weight_gender_balance'
            )
        }),
        ('Calculated Metrics', {
            'fields': (
                'portfolio_quality_score', 'portfolio_risk_score',
                'representativeness_score', 'equality_score', 'gender_balance_score',
                'metrics_last_calculated'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )


@admin.register(SubmissionOutput)
class SubmissionOutputAdmin(admin.ModelAdmin):
    list_display = ['submission', 'output', 'order', 'is_reserve', 'strategic_importance']
    list_filter = ['is_reserve', 'strategic_importance', 'submission']
    search_fields = ['submission__name', 'output__title']


# Access Control Admin
from .admin_access_control import *
