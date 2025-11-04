from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse


class Colleague(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=20, blank=True)
    
    fte = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(0.1), MaxValueValidator(1.0)],
        help_text="Full-time equivalent (0.1 to 1.0)"
    )
    contract_type = models.CharField(
        max_length=50,
        choices=[
            ('permanent', 'Permanent'),
            ('fixed-term', 'Fixed Term'),
            ('research', 'Research Only'),
        ],
        default='permanent'
    )
    
    # NEW FIELDS - Employment Status
    EMPLOYMENT_STATUS_CHOICES = [
        ('current', 'Current Staff'),
        ('former', 'Former Staff'),
    ]
    
    employment_status = models.CharField(
        max_length=10,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='current',
        help_text='Whether this person is currently employed or a former staff member'
    )
    
    employment_end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when employment ended (for former staff)'
    )
 
    COLLEAGUE_CATEGORY_CHOICES = [
    ('independent', 'Independent Researcher'),
    ('non_independent', 'Non Independent Researcher'),  # UNDERSCORE only
    ('postdoc', 'Post-Doctoral Researcher'),
    ('research_assistant', 'Research Assistant'),
    ('academic', 'Academic Staff'),
    ('support', 'Support Staff'),
    ('employee', 'Current Employee'),
    ('former', 'Former Employee'),
    ('coauthor', 'Co-author (External)'),
]
 
    colleague_category = models.CharField(
        max_length=50,
        choices=COLLEAGUE_CATEGORY_CHOICES,
        default='independent',
        help_text='Category of colleague for REF purposes',
        verbose_name='Colleague Category'
)  
         
    unit_of_assessment = models.CharField(max_length=100)
    is_returnable = models.BooleanField(default=True)
    submission_group = models.CharField(max_length=100, blank=True)
    
    office = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        # Updated to show former status
        status = " (Former)" if self.employment_status == 'former' else ""
        return f"{self.user.get_full_name()} ({self.staff_id}){status}"
    
    def get_absolute_url(self):
        return reverse('colleague_detail', kwargs={'pk': self.pk})
    
    # NEW METHOD
    def is_current_staff(self):
        """Check if this is a current staff member"""
        return self.employment_status == 'current'


    @property
    def required_outputs(self):
        if self.fte >= 0.2:
            return min(int(float(self.fte) * 2.5), 5)
        return 0
    

    @property
    def submitted_outputs_count(self):
        return self.outputs.filter(status='approved').count()
    
    @property
    def completion_percentage(self):
        required = self.required_outputs
        if required == 0:
            return 100
        return min(int((self.submitted_outputs_count / required) * 100), 100)


class Output(models.Model):
    QUALITY_CHOICES = [
        ('4*', '4* - World-leading'),
        ('3*', '3* - Internationally excellent'),
        ('2*', '2* - Recognized internationally'),
        ('1*', '1* - Recognized nationally'),
        ('U', 'Unclassified'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('internal-review', 'Internal Review'),
        ('external-review', 'External Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revision', 'Needs Revision'),
    ]
    
    PUBLICATION_TYPES = [
        ('A', 'Journal Article'),
        ('B', 'Book'),
        ('C', 'Book Chapter'),
        ('D', 'Conference Paper'),
        ('E', 'Patent'),
        ('F', 'Software'),
        ('G', 'Performance/Exhibition'),
        ('H', 'Other'),
    ]
    
    colleague = models.ForeignKey(Colleague, on_delete=models.CASCADE, related_name='outputs')
    title = models.CharField(max_length=500)
    publication_type = models.CharField(max_length=1, choices=PUBLICATION_TYPES)
    
    publication_date = models.DateField()
    publication_venue = models.CharField(max_length=300, blank=True)
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    pages = models.CharField(max_length=50, blank=True)
    
    doi = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=50, blank=True)
    url = models.URLField(max_length=500, blank=True)
    
    all_authors = models.TextField(help_text="All authors in citation format")
    author_position = models.IntegerField(
        help_text="Position of colleague in author list",
        validators=[MinValueValidator(1)]
    )
    
    uoa = models.CharField(max_length=100, verbose_name="Unit of Assessment")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    quality_rating = models.CharField(
        max_length=2, 
        choices=QUALITY_CHOICES, 
        blank=True,
        help_text="Internal quality assessment"
    )
    
    is_double_weighted = models.BooleanField(default=False)
    is_interdisciplinary = models.BooleanField(default=False)
    is_open_access = models.BooleanField(default=False)
    
    pdf_file = models.FileField(upload_to='outputs/', blank=True, null=True)
    supplementary_file = models.FileField(upload_to='outputs/supplementary/', blank=True, null=True)
    
    abstract = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    
    internal_notes = models.TextField(blank=True)
    
    submitted_date = models.DateTimeField(null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-publication_date']
        verbose_name_plural = "Outputs"
    
    def __str__(self):
        return f"{self.title[:50]} - {self.colleague.user.get_full_name()}"
    
    def get_absolute_url(self):
        return reverse('output_detail', kwargs={'pk': self.pk})
    
    @property
    def citation(self):
        return f"{self.all_authors} ({self.publication_date.year}). {self.title}. {self.publication_venue}."


class CriticalFriend(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('limited', 'Limited Availability'),
        ('busy', 'Currently Busy'),
        ('unavailable', 'Unavailable'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField(validators=[EmailValidator()])
    institution = models.CharField(max_length=300)
    department = models.CharField(max_length=200, blank=True)
    
    expertise_areas = models.TextField(help_text="Comma-separated list")
    research_interests = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    orcid = models.CharField(max_length=50, blank=True)
    
    is_internal = models.BooleanField(
        default=False,
        help_text="Check if this reviewer is part of your internal panel (not an external critical friend)"
    )
    
    availability = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('limited', 'Limited Availability'),
            ('unavailable', 'Unavailable'),
        ],
        default='available'
    )
    
    max_assignments = models.IntegerField(default=5)
    notes = models.TextField(blank=True)
    
    user_account = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='critical_friend_profile'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Critical Friend / Internal Reviewer"
        verbose_name_plural = "Critical Friends / Internal Reviewers"
        ordering = ['name']
    
    def __str__(self):
        reviewer_type = "Internal Panel" if self.is_internal else "Critical Friend"
        return f"{self.name} ({reviewer_type})"
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.institution})"
    
    def get_absolute_url(self):
        return reverse('critical_friend_detail', kwargs={'pk': self.pk})
    
    @property
    def current_workload(self):
        return self.assignments.filter(
            status__in=['assigned', 'accepted', 'in-progress']
        ).count()
    
    @property
    def completed_reviews(self):
        return self.assignments.filter(status='completed').count()
    
    @property
    def is_available_for_assignment(self):
        return (
            self.availability in ['available', 'limited'] and 
            self.current_workload < self.max_assignments
        )


class CriticalFriendAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
    ]
    
    QUALITY_CHOICES = Output.QUALITY_CHOICES
    
    output = models.ForeignKey(
        Output, 
        on_delete=models.CASCADE,
        related_name='critical_friend_reviews'
    )
    critical_friend = models.ForeignKey(
        CriticalFriend,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    accepted_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    quality_assessment = models.CharField(max_length=2, choices=QUALITY_CHOICES, blank=True)
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    overall_comments = models.TextField(blank=True)
    
    originality_score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    significance_score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    rigour_score = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    internal_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-assigned_date']
        unique_together = ['output', 'critical_friend']
    
    def __str__(self):
        return f"{self.critical_friend.name} - {self.output.title[:30]}"
    
    @property
    def is_overdue(self):
        if self.status in ['completed', 'declined']:
            return False
        return timezone.now().date() > self.due_date


class Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    from_entity = models.CharField(max_length=200)
    subject = models.CharField(max_length=500)
    description = models.TextField()
    
    deadline = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_requests'
    )
    
    response = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-deadline', '-priority']
    
    def __str__(self):
        return f"{self.subject} - {self.from_entity}"
    
    @property
    def is_overdue(self):
        if self.status == 'completed':
            return False
        return timezone.now().date() > self.deadline


class InternalReview(models.Model):
    output = models.ForeignKey(Output, on_delete=models.CASCADE, related_name='internal_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    quality_assessment = models.CharField(max_length=2, choices=Output.QUALITY_CHOICES)
    comments = models.TextField()
    recommendations = models.TextField(blank=True)
    
    reviewed_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-reviewed_date']
    
    def __str__(self):
        return f"Internal review by {self.reviewer.get_full_name()}"


class InternalPanelMember(models.Model):
    """Internal evaluation panel member"""
    colleague = models.ForeignKey(Colleague, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=100,
        choices=[
            ('chair', 'Panel Chair'),
            ('member', 'Panel Member'),
            ('specialist', 'Subject Specialist'),
            ('external_liaison', 'External Liaison'),
        ],
        default='member'
    )
    expertise_area = models.CharField(max_length=200)
    appointed_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Internal Panel Member'
        verbose_name_plural = 'Internal Panel Members'
    
    def __str__(self):
        return f"{self.colleague.user.get_full_name()} ({self.get_role_display()})"


class InternalPanelAssignment(models.Model):
    """Assignment of internal panel member to an output"""
    output = models.ForeignKey(Output, on_delete=models.CASCADE, related_name='internal_panel_assignments')
    panel_member = models.ForeignKey(InternalPanelMember, on_delete=models.CASCADE)
    assigned_date = models.DateField(default=timezone.now)
    review_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('assigned', 'Assigned'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('deferred', 'Deferred'),
        ],
        default='assigned'
    )
    rating_recommendation = models.CharField(
        max_length=2,
        choices=Output.QUALITY_CHOICES,
        blank=True
    )
    comments = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Internal Panel Assignment'
        verbose_name_plural = 'Internal Panel Assignments'
        unique_together = ['output', 'panel_member']
    
    def __str__(self):
        return f"{self.panel_member} reviewing {self.output.title[:50]}"

    

# Add this new model to your core/models.py:
class Task(models.Model):
    """General tasks for REF submission management"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CATEGORY_CHOICES = [
        ('administrative', 'Administrative'),
        ('submission', 'Submission'),
        ('review', 'Review'),
        ('meeting', 'Meeting'),
        ('documentation', 'Documentation'),
        ('deadline', 'Deadline'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )
    
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True, help_text="Additional notes or updates")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'due_date', '-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status in ['completed', 'cancelled']:
            return False
        if self.due_date:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - timezone.now().date()
        return delta.days
    
    def mark_completed(self):
        """Mark task as completed"""
        self.status = 'completed'
        self.completed_date = timezone.now()
        self.save()
    
    def get_priority_class(self):
        """Return CSS class for priority badge"""
        return {
            'low': 'secondary',
            'medium': 'info',
            'high': 'warning',
            'urgent': 'danger'
        }.get(self.priority, 'secondary')
    
    def get_status_class(self):
        """Return CSS class for status badge"""
        return {
            'pending': 'secondary',
            'in_progress': 'primary',
            'completed': 'success',
            'cancelled': 'dark'
        }.get(self.status, 'secondary')

    
