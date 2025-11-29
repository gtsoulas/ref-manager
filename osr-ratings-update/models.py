from django.db import models
from decimal import Decimal
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
        ('aside', 'Set aside for now'),
        ('planning', 'In Planning'),
        ('ready', 'Ready to Submit'),
        ('reserve', 'Reserve')
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
    publication_year = models.IntegerField(
    validators=[MinValueValidator(2021), MaxValueValidator(2028)],
    help_text="Year of publication (e.g., 2024)"
)
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
    # Separate quality ratings from different reviewers

    quality_rating_internal = models.CharField(

        max_length=2,

        choices=QUALITY_CHOICES,

        blank=True,

        verbose_name="Internal Panel Rating",

        help_text="Quality assessment from internal panel"

    )

    

    quality_rating_external = models.CharField(

        max_length=2,

        choices=QUALITY_CHOICES,

        blank=True,

        verbose_name="Critical Friend Rating",

        help_text="Quality assessment from critical friends"

    )
    
    quality_rating_self = models.CharField(
        max_length=2,
        choices=QUALITY_CHOICES,
        blank=True,
        verbose_name="Self-Assessment Rating",
        help_text="Author's own quality assessment"
    )

    

    quality_rating_average = models.CharField(

        max_length=2,

        choices=QUALITY_CHOICES,

        blank=True,

        verbose_name="Average Rating",

        help_text="Calculated average of internal and external ratings"

    )

    

    # Keep old field for backwards compatibility

    quality_rating = models.CharField(

        max_length=2,

        choices=QUALITY_CHOICES,

        blank=True,

        verbose_name="Overall Rating (Deprecated)"

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
    # ========== RISK ASSESSMENT FIELDS (Added by setup script) ==========
    
    content_risk_score = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Risk of panel disagreement with methodology/approach (0-1 scale)"
    )
    
    content_risk_rationale = models.TextField(
        blank=True,
        help_text="Explain why this output might face panel disagreement or concerns"
    )
    
    timeline_risk_score = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Risk of publication delay (0=published, 1=planning stage)"
    )
    
    overall_risk_score = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Calculated composite risk score"
    )
    
    risk_content_weight = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=Decimal('0.60'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Weight for content risk (default 0.6)"
    )
    
    risk_timeline_weight = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=Decimal('0.40'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Weight for timeline risk (default 0.4)"
    )
    
    oa_compliance_risk = models.BooleanField(
        default=False,
        help_text="Is there Open Access compliance risk? (Critical for REF)"
    )
    
    oa_compliance_notes = models.TextField(
        blank=True,
        help_text="Details about OA compliance status or concerns"
    )
    
    panel_alignment_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="How well does this align with panel expertise? (1=perfect, 0=poor)"
    )
    
    panel_alignment_notes = models.TextField(
        blank=True,
        help_text="Notes on panel alignment concerns or alternative UOA considerations"
    )
    
    venue_prestige_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.50'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Journal/venue prestige and reputation (0=low, 1=high)"
    )
    
    interdisciplinary_flag = models.BooleanField(
        default=False,
        help_text="Is this interdisciplinary work? (May receive additional weighting)"
    )
    
    risk_last_calculated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When risk scores were last calculated"
    )

    def calculate_overall_risk(self):
        """Calculate composite risk score from content and timeline risks."""
        from django.utils import timezone
        
        total_weight = self.risk_content_weight + self.risk_timeline_weight
        if total_weight == 0:
            self.overall_risk_score = Decimal('0.00')
        else:
            content_w = self.risk_content_weight / total_weight
            timeline_w = self.risk_timeline_weight / total_weight
            
            self.overall_risk_score = (
                self.content_risk_score * content_w +
                self.timeline_risk_score * timeline_w
            )
        
        if self.oa_compliance_risk:
            self.overall_risk_score = max(self.overall_risk_score, Decimal('0.85'))
        
        self.risk_last_calculated = timezone.now()
        return self.overall_risk_score
    
    def auto_set_timeline_risk(self):
        """Automatically set timeline risk based on publication status."""
        risk_mapping = {
            'published': Decimal('0.00'),
            'accepted': Decimal('0.20'),
            'under-review': Decimal('0.50'),
            'in-revision': Decimal('0.70'),
            'in-preparation': Decimal('0.90'),
            'planned': Decimal('1.00')
        }
        
        current_status = getattr(self, 'status', 'planned')
        self.timeline_risk_score = risk_mapping.get(current_status, Decimal('0.50'))
        return self.timeline_risk_score
    
    def get_risk_level(self):
        """Return risk category as string."""
        risk = self.overall_risk_score
        if risk < Decimal('0.25'):
            return 'low'
        elif risk < Decimal('0.50'):
            return 'medium-low'
        elif risk < Decimal('0.75'):
            return 'medium-high'
        else:
            return 'high'
    
    def get_risk_level_display(self):
        """Return human-readable risk level"""
        levels = {
            'low': 'Low Risk',
            'medium-low': 'Medium-Low Risk',
            'medium-high': 'Medium-High Risk',
            'high': 'High Risk'
        }
        return levels.get(self.get_risk_level(), 'Unknown')
    
    def get_risk_color(self):
        """Return CSS color code for risk visualization"""
        level = self.get_risk_level()
        colors = {
            'low': '#28a745',
            'medium-low': '#ffc107',
            'medium-high': '#fd7e14',
            'high': '#dc3545'
        }
        return colors.get(level, '#6c757d')
    
    def get_risk_summary(self):
        """Return a dictionary with comprehensive risk information"""
        return {
            'overall_score': float(self.overall_risk_score),
            'level': self.get_risk_level(),
            'level_display': self.get_risk_level_display(),
            'color': self.get_risk_color(),
            'content_risk': float(self.content_risk_score),
            'timeline_risk': float(self.timeline_risk_score),
            'oa_compliance_risk': self.oa_compliance_risk,
            'panel_alignment': float(self.panel_alignment_score),
            'venue_prestige': float(self.venue_prestige_score),
            'needs_mitigation': self.overall_risk_score >= Decimal('0.75'),
            'last_calculated': self.risk_last_calculated,
        }
    
    def get_quality_value(self):
        """Convert star rating to numeric value for calculations"""
        quality_map = {
            '1*': 1,
            '2*': 2,
            '3*': 3,
            '4*': 4,
            'unclassified': 0
        }
        rating = getattr(self, 'quality_rating', 'unclassified')
        return quality_map.get(rating, 0)
    
    def is_ref_ready(self):
        """Determine if output is ready for REF submission"""
        return (
            self.overall_risk_score < Decimal('0.50') and
            not self.oa_compliance_risk and
            self.get_quality_value() >= 3
        )

    
    class Meta:
        ordering = ['-publication_year']
        verbose_name_plural = "Outputs"
    
    def __str__(self):
        return f"{self.title[:50]} - {self.colleague.user.get_full_name()}"
    
    def get_absolute_url(self):
        return reverse('output_detail', kwargs={'pk': self.pk})
    
    @property
    def citation(self):
        return f"{self.all_authors} ({self.publication_year}). {self.title}. {self.publication_venue}."

    def calculate_average_rating(self, include_self=False):
        """
        Calculate average quality rating from assessments.
        
        Args:
            include_self: If True, includes self-evaluation in average
        """
        ratings_map = {
            '4*': 4,
            '3*': 3,
            '2*': 2,
            '1*': 1,
            'U': 0
        }
        
        reverse_map = {4: '4*', 3: '3*', 2: '2*', 1: '1*', 0: 'U'}
        
        ratings = []
        
        # Include internal rating if exists
        if self.quality_rating_internal:
            ratings.append(ratings_map.get(self.quality_rating_internal, 0))
        
        # Include external rating if exists
        if self.quality_rating_external:
            ratings.append(ratings_map.get(self.quality_rating_external, 0))
        
        # Include self-evaluation if requested AND it exists
        if include_self and self.quality_rating_self:
            ratings.append(ratings_map.get(self.quality_rating_self, 0))
        
        # Calculate average if we have at least one rating
        if ratings:
            avg = sum(ratings) / len(ratings)
            avg_rounded = round(avg)
            self.quality_rating_average = reverse_map.get(avg_rounded, 'U')
            return self.quality_rating_average
        
        # No ratings available - return empty
        self.quality_rating_average = ''
        return ''
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate average rating"""
        # Calculate average - set include_self=True to include self-evaluation
        self.calculate_average_rating(include_self=True)
        # Call parent save
        super().save(*args, **kwargs)
    
    def get_average_excluding_self(self):
        """Get average of internal and external ratings only (excludes self-assessment)"""
        ratings_map = {'4*': 4, '3*': 3, '2*': 2, '1*': 1, 'U': 0}
        reverse_map = {4: '4*', 3: '3*', 2: '2*', 1: '1*', 0: 'U'}
        
        ratings = []
        if self.quality_rating_internal:
            ratings.append(ratings_map.get(self.quality_rating_internal, 0))
        if self.quality_rating_external:
            ratings.append(ratings_map.get(self.quality_rating_external, 0))
        
        if ratings:
            avg = sum(ratings) / len(ratings)
            avg_rounded = round(avg)
            return reverse_map.get(avg_rounded, 'U')
        return ''

    def get_average_including_self(self):
        """Get average of all three ratings (includes self-assessment)"""
        ratings_map = {'4*': 4, '3*': 3, '2*': 2, '1*': 1, 'U': 0}
        reverse_map = {4: '4*', 3: '3*', 2: '2*', 1: '1*', 0: 'U'}
        
        ratings = []
        if self.quality_rating_internal:
            ratings.append(ratings_map.get(self.quality_rating_internal, 0))
        if self.quality_rating_external:
            ratings.append(ratings_map.get(self.quality_rating_external, 0))
        if self.quality_rating_self:
            ratings.append(ratings_map.get(self.quality_rating_self, 0))
        
        if ratings:
            avg = sum(ratings) / len(ratings)
            avg_rounded = round(avg)
            return reverse_map.get(avg_rounded, 'U')
        return ''

    def get_rating_color_class(self, rating):
        """Get Bootstrap color class for a rating"""
        if rating == '4*':
            return 'success'
        elif rating == '3*':
            return 'info'
        elif rating == '2*':
            return 'warning'
        elif rating == '1*':
            return 'secondary'
        else:
            return 'light text-dark'

    # ========== THREE-COMPONENT DECIMAL RATING METHODS ==========
    
    def get_internal_panel_osr_average(self):
        """
        Calculate average O/S/R rating across all Internal Panel assignments.
        Returns a Decimal or None if no ratings exist.
        """
        from decimal import Decimal, ROUND_HALF_UP
        
        assignments = self.internal_panel_assignments.all()
        all_ratings = []
        
        for assignment in assignments:
            if assignment.component_average_rating is not None:
                all_ratings.append(assignment.component_average_rating)
        
        if all_ratings:
            avg = sum(all_ratings) / len(all_ratings)
            return Decimal(str(avg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return None
    
    def get_critical_friend_osr_average(self):
        """
        Calculate average O/S/R rating across all Critical Friend assignments.
        Returns a Decimal or None if no ratings exist.
        """
        from decimal import Decimal, ROUND_HALF_UP
        
        assignments = self.critical_friend_reviews.all()
        all_ratings = []
        
        for assignment in assignments:
            if assignment.component_average_rating is not None:
                all_ratings.append(assignment.component_average_rating)
        
        if all_ratings:
            avg = sum(all_ratings) / len(all_ratings)
            return Decimal(str(avg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return None
    
    def get_combined_osr_average(self, include_self=False):
        """
        Calculate combined O/S/R average across Internal Panel and Critical Friend.
        
        Args:
            include_self: If True, includes self-assessment quality_rating_self 
                          (converted to decimal scale 0-4)
        
        Returns a Decimal or None if no ratings exist.
        """
        from decimal import Decimal, ROUND_HALF_UP
        
        all_ratings = []
        
        # Get Internal Panel ratings
        internal_avg = self.get_internal_panel_osr_average()
        if internal_avg is not None:
            all_ratings.append(internal_avg)
        
        # Get Critical Friend ratings
        cf_avg = self.get_critical_friend_osr_average()
        if cf_avg is not None:
            all_ratings.append(cf_avg)
        
        # Include self-assessment if requested (convert star rating to decimal)
        if include_self and self.quality_rating_self:
            self_map = {'4*': Decimal('4.00'), '3*': Decimal('3.00'), 
                        '2*': Decimal('2.00'), '1*': Decimal('1.00'), 'U': Decimal('0.00')}
            self_rating = self_map.get(self.quality_rating_self)
            if self_rating is not None:
                all_ratings.append(self_rating)
        
        if all_ratings:
            avg = sum(all_ratings) / len(all_ratings)
            return Decimal(str(avg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return None
    
    def get_osr_breakdown(self):
        """
        Get detailed O/S/R breakdown across all reviewers.
        Returns dict with average O, S, R values and overall average.
        """
        from decimal import Decimal, ROUND_HALF_UP
        
        o_ratings = []
        s_ratings = []
        r_ratings = []
        
        # Collect from Internal Panel
        for assignment in self.internal_panel_assignments.all():
            if assignment.originality_rating is not None:
                o_ratings.append(assignment.originality_rating)
            if assignment.significance_rating is not None:
                s_ratings.append(assignment.significance_rating)
            if assignment.rigour_rating is not None:
                r_ratings.append(assignment.rigour_rating)
        
        # Collect from Critical Friends
        for assignment in self.critical_friend_reviews.all():
            if assignment.originality_rating is not None:
                o_ratings.append(assignment.originality_rating)
            if assignment.significance_rating is not None:
                s_ratings.append(assignment.significance_rating)
            if assignment.rigour_rating is not None:
                r_ratings.append(assignment.rigour_rating)
        
        def calc_avg(ratings):
            if ratings:
                avg = sum(ratings) / len(ratings)
                return Decimal(str(avg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return None
        
        o_avg = calc_avg(o_ratings)
        s_avg = calc_avg(s_ratings)
        r_avg = calc_avg(r_ratings)
        
        # Overall average
        component_avgs = [a for a in [o_avg, s_avg, r_avg] if a is not None]
        overall = calc_avg(component_avgs) if component_avgs else None
        
        return {
            'originality': o_avg,
            'significance': s_avg,
            'rigour': r_avg,
            'overall': overall,
            'o_count': len(o_ratings),
            's_count': len(s_ratings),
            'r_count': len(r_ratings),
        }

    def get_combined_osr_average_with_self(self):
        """
        Wrapper method for templates - gets combined O/S/R average including self-assessment.
        """
        return self.get_combined_osr_average(include_self=True)


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

    REVIEWER_TYPE_CHOICES = [
    ('specialist', 'Specialist'),
    ('non-specialist', 'Non-Specialist'),
]

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
    reviewer_type = models.CharField(
    max_length=20,
    choices=REVIEWER_TYPE_CHOICES,
    default='specialist',
    verbose_name="Reviewer Expertise Type",
    help_text="Is this critical friend a specialist in this research area?"
)
    quality_assessment = models.CharField(max_length=2, choices=QUALITY_CHOICES, blank=True)
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    overall_comments = models.TextField(blank=True)
    
    # Three-component ratings (v3.1 - decimal scale 0.00-4.00)
    originality_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        verbose_name='Originality', help_text='Rate originality from 0.00 to 4.00'
    )
    significance_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        verbose_name='Significance', help_text='Rate significance from 0.00 to 4.00'
    )
    rigour_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        verbose_name='Rigour', help_text='Rate rigour from 0.00 to 4.00'
    )
    component_average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        verbose_name='Average Rating', help_text='Calculated average of O/S/R'
    )
    confidential_comments = models.TextField(
        blank=True, verbose_name='Confidential Comments',
        help_text='Visible only to administrators and observers'
    )
    
    internal_notes = models.TextField(blank=True)

    def calculate_component_average(self):
        from decimal import Decimal, ROUND_HALF_UP
        ratings = [r for r in [self.originality_rating, self.significance_rating, self.rigour_rating] if r is not None]
        if ratings:
            avg = sum(ratings) / len(ratings)
            return Decimal(str(avg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return None
    
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
    
    # Add reviewer type choices
    REVIEWER_TYPE_CHOICES = [
        ('specialist', 'Specialist'),
        ('non-specialist', 'Non-Specialist'),
    ]
    
    output = models.ForeignKey(Output, on_delete=models.CASCADE, related_name='internal_panel_assignments')
    panel_member = models.ForeignKey(InternalPanelMember, on_delete=models.CASCADE)
    
    # NEW FIELD: Reviewer expertise type
    reviewer_type = models.CharField(
        max_length=20,
        choices=REVIEWER_TYPE_CHOICES,
        default='specialist',
        verbose_name="Reviewer Expertise Type",
        help_text="Is this panel member a specialist in this research area?"
    )
    
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
        
    # Three-component ratings (v3.1)
    originality_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        verbose_name='Originality', help_text='Rate originality from 0.00 to 4.00'
    )
    significance_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        verbose_name='Significance', help_text='Rate significance from 0.00 to 4.00'
    )
    rigour_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        verbose_name='Rigour', help_text='Rate rigour from 0.00 to 4.00'
    )
    component_average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        verbose_name='Average Rating', help_text='Calculated average of O/S/R'
    )
    confidential_comments = models.TextField(
        blank=True, verbose_name='Confidential Comments',
        help_text='Visible only to administrators, observers, and panel members'
    )

    def calculate_component_average(self):
        from decimal import Decimal, ROUND_HALF_UP
        ratings = [r for r in [self.originality_rating, self.significance_rating, self.rigour_rating] if r is not None]
        if ratings:
            avg = sum(ratings) / len(ratings)
            return Decimal(str(avg)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return None

    def save(self, *args, **kwargs):
        self.component_average_rating = self.calculate_component_average()
        super().save(*args, **kwargs)
    
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

    


class REFSubmission(models.Model):
    """
    A portfolio of outputs forming a REF submission.
    Tracks quality, risk, and diversity metrics for the entire submission.
    """
    
    name = models.CharField(
        max_length=200,
        help_text="Name for this submission scenario (e.g., 'Main Submission v2', 'Conservative Strategy')"
    )
    
    uoa = models.CharField(
        max_length=100,
        verbose_name="Unit of Assessment",
        help_text="Which UOA this submission is for (e.g., 'UOA 25 - Modern Languages')"
    )
    
    submission_year = models.IntegerField(
        default=2029,
        help_text="REF submission year"
    )
    
    outputs = models.ManyToManyField(
        'Output',
        through='SubmissionOutput',
        related_name='ref_submissions',
        help_text="Outputs included in this submission"
    )
    
    # ========== CALCULATED PORTFOLIO METRICS ==========
    
    portfolio_quality_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Average quality score (GPA calculation)"
    )
    
    portfolio_risk_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Portfolio risk score (inverted: 1 = low risk, 0 = high risk)"
    )
    
    representativeness_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="How well submission represents departmental research areas"
    )
    
    equality_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Percentage of eligible staff submitted (0-100)"
    )
    
    gender_balance_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Gender balance metric (1 = perfect balance, 0 = severe imbalance)"
    )
    
    ecr_representation_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Early Career Researcher representation score"
    )
    
    interdisciplinary_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Proportion of interdisciplinary outputs"
    )
    
    # ========== OPTIMIZATION WEIGHTS ==========
    
    weight_quality = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.40'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Weight for quality in portfolio score"
    )
    
    weight_risk = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.25'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Weight for risk management in portfolio score"
    )
    
    weight_representativeness = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.15'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Weight for research area representation"
    )
    
    weight_equality = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.10'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Weight for staff inclusion"
    )
    
    weight_gender_balance = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.10'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Weight for gender balance"
    )
    
    # ========== METADATA ==========
    
    description = models.TextField(
        blank=True,
        help_text="Description of this submission strategy"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this an active submission scenario?"
    )
    
    is_final = models.BooleanField(
        default=False,
        help_text="Is this the final submission?"
    )
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_submissions'
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this submission"
    )
    
    metrics_last_calculated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When portfolio metrics were last calculated"
    )
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = "REF Submission"
        verbose_name_plural = "REF Submissions"
    
    def __str__(self):
        return f"{self.name} ({self.uoa}, {self.submission_year})"
    
    def get_absolute_url(self):
        return reverse('submission-detail', kwargs={'pk': self.pk})
    
    # ========== PORTFOLIO CALCULATION METHODS ==========
    
    def calculate_portfolio_quality(self):
        """
        Calculate average quality score using REF GPA method.
        4* = 4 points, 3* = 3 points, etc.
        """
        submission_outputs = self.submissionoutput_set.select_related('output')
        
        if not submission_outputs.exists():
            self.portfolio_quality_score = Decimal('0.00')
            return self.portfolio_quality_score
        
        total_points = sum(so.output.get_quality_value() for so in submission_outputs)
        count = submission_outputs.count()
        
        self.portfolio_quality_score = Decimal(str(total_points / count)) if count > 0 else Decimal('0.00')
        return self.portfolio_quality_score
    
    def calculate_portfolio_risk(self):
        """
        Calculate portfolio risk score (inverted: 1 = low risk, 0 = high risk).
        Average of all output risks, then inverted.
        """
        submission_outputs = self.submissionoutput_set.select_related('output')
        
        if not submission_outputs.exists():
            self.portfolio_risk_score = Decimal('0.00')
            return self.portfolio_risk_score
        
        total_risk = sum(so.output.overall_risk_score for so in submission_outputs)
        count = submission_outputs.count()
        avg_risk = total_risk / count if count > 0 else Decimal('0.00')
        
        # Invert risk: low risk outputs give high portfolio score
        self.portfolio_risk_score = Decimal('1.00') - avg_risk
        return self.portfolio_risk_score
    
    def calculate_representativeness(self):
        """
        Calculate how well submission represents departmental research areas.
        This is a placeholder - customize based on your research area taxonomy.
        """
        # You'll need to implement this based on your Output model's research area fields
        # For now, return a default score
        self.representativeness_score = Decimal('0.75')
        return self.representativeness_score
    
    def calculate_equality(self):
        """
        Calculate percentage of eligible staff included in submission.
        """
        from django.db.models import Count
        
        # Count unique staff members in this submission
        staff_count = self.outputs.values('colleague').distinct().count()
        
        # Get total eligible staff (adjust based on your model structure)
        # This assumes Colleague model exists and has an 'eligible_for_ref' field
        try:
            from .models import Colleague
            total_eligible = Colleague.objects.filter(eligible_for_ref=True).count()
        except:
            total_eligible = 1  # Avoid division by zero
        
        if total_eligible > 0:
            self.equality_score = Decimal(str((staff_count / total_eligible) * 100))
        else:
            self.equality_score = Decimal('0.00')
        
        return self.equality_score
    
    def calculate_gender_balance(self):
        """
        Calculate gender balance metric.
        1.0 = perfect 50/50 balance, 0.0 = severe imbalance
        """
        # This is a placeholder - implement based on your Colleague model
        # For now, return a reasonable default
        self.gender_balance_score = Decimal('0.80')
        return self.gender_balance_score
    
    def calculate_all_metrics(self):
        """
        Calculate all portfolio metrics and save.
        """
        self.calculate_portfolio_quality()
        self.calculate_portfolio_risk()
        self.calculate_representativeness()
        self.calculate_equality()
        self.calculate_gender_balance()
        
        # Calculate ECR and interdisciplinary scores
        submission_outputs = self.submissionoutput_set.select_related('output')
        total = submission_outputs.count()
        
        if total > 0:
            # ECR representation (placeholder - adjust based on your model)
            ecr_count = sum(1 for so in submission_outputs if getattr(so.output.colleague, 'is_ecr', False))
            self.ecr_representation_score = Decimal(str(ecr_count / total))
            
            # Interdisciplinary outputs
            interdisciplinary_count = sum(1 for so in submission_outputs if so.output.interdisciplinary_flag)
            self.interdisciplinary_score = Decimal(str(interdisciplinary_count / total))
        
        self.metrics_last_calculated = timezone.now()
        self.save()
    
    def get_overall_portfolio_score(self):
        """
        Calculate weighted portfolio score using all metrics and weights.
        Returns a score from 0-4 (aligned with REF GPA scale).
        """
        # Ensure weights sum to 1.0
        total_weight = (
            self.weight_quality +
            self.weight_risk +
            self.weight_representativeness +
            self.weight_equality +
            self.weight_gender_balance
        )
        
        if total_weight == 0:
            return Decimal('0.00')
        
        # Normalize weights
        weights = {
            'quality': self.weight_quality / total_weight,
            'risk': self.weight_risk / total_weight,
            'representativeness': self.weight_representativeness / total_weight,
            'equality': self.weight_equality / total_weight,
            'gender_balance': self.weight_gender_balance / total_weight,
        }
        
        # Calculate weighted score
        score = (
            self.portfolio_quality_score * weights['quality'] +
            self.portfolio_risk_score * Decimal('4.00') * weights['risk'] +  # Scale risk to 0-4
            self.representativeness_score * Decimal('4.00') * weights['representativeness'] +
            (self.equality_score / Decimal('25.00')) * weights['equality'] +  # Scale 0-100 to 0-4
            self.gender_balance_score * Decimal('4.00') * weights['gender_balance']
        )
        
        return score
    
    # ========== RISK ANALYSIS METHODS ==========
    
    def get_risk_distribution(self):
        """
        Return count of outputs by risk level.
        """
        outputs = self.outputs.all()
        return {
            'low': outputs.filter(overall_risk_score__lt=Decimal('0.25')).count(),
            'medium_low': outputs.filter(
                overall_risk_score__gte=Decimal('0.25'),
                overall_risk_score__lt=Decimal('0.50')
            ).count(),
            'medium_high': outputs.filter(
                overall_risk_score__gte=Decimal('0.50'),
                overall_risk_score__lt=Decimal('0.75')
            ).count(),
            'high': outputs.filter(overall_risk_score__gte=Decimal('0.75')).count(),
        }
    
    def get_quality_distribution(self):
        """
        Return count of outputs by quality rating.
        """
        outputs = self.outputs.all()
        return {
            '4*': outputs.filter(quality_rating='4*').count(),
            '3*': outputs.filter(quality_rating='3*').count(),
            '2*': outputs.filter(quality_rating='2*').count(),
            '1*': outputs.filter(quality_rating='1*').count(),
            'unclassified': outputs.filter(quality_rating='unclassified').count(),
        }
    
    def get_high_risk_outputs(self):
        """Return outputs with high risk (≥0.75)"""
        return self.outputs.filter(overall_risk_score__gte=Decimal('0.75'))
    
    def get_medium_high_risk_outputs(self):
        """Return outputs with medium-high risk (0.50-0.75)"""
        return self.outputs.filter(
            overall_risk_score__gte=Decimal('0.50'),
            overall_risk_score__lt=Decimal('0.75')
        )
    
    def get_low_risk_outputs(self):
        """Return outputs with low risk (<0.25)"""
        return self.outputs.filter(overall_risk_score__lt=Decimal('0.25'))
    
    def get_four_star_outputs(self):
        """Return 4* outputs"""
        return self.outputs.filter(quality_rating='4*')
    
    def get_three_four_star_outputs(self):
        """Return 3* and 4* outputs combined"""
        return self.outputs.filter(quality_rating__in=['3*', '4*'])
    
    def has_oa_compliance_issues(self):
        """Check if any outputs have OA compliance risks"""
        return self.outputs.filter(oa_compliance_risk=True).exists()
    
    def get_oa_compliance_issues(self):
        """Return outputs with OA compliance risks"""
        return self.outputs.filter(oa_compliance_risk=True)
    
    def get_submission_readiness(self):
        """
        Return overall submission readiness assessment.
        """
        total = self.outputs.count()
        if total == 0:
            return {
                'ready': False,
                'readiness_percentage': 0,
                'issues': ['No outputs in submission'],
            }
        
        ready_count = sum(1 for o in self.outputs.all() if o.is_ref_ready())
        readiness_pct = (ready_count / total) * 100
        
        issues = []
        if self.has_oa_compliance_issues():
            issues.append('OA compliance issues detected')
        if self.get_high_risk_outputs().count() > total * 0.2:
            issues.append('More than 20% of outputs are high risk')
        if self.portfolio_quality_score < Decimal('3.00'):
            issues.append('Portfolio quality below 3* average')
        
        return {
            'ready': len(issues) == 0 and readiness_pct >= 80,
            'readiness_percentage': readiness_pct,
            'ready_outputs': ready_count,
            'total_outputs': total,
            'issues': issues,
        }


class SubmissionOutput(models.Model):
    """
    Through model linking outputs to submissions.
    Allows tracking of output-specific submission information.
    """
    
    submission = models.ForeignKey(
        REFSubmission,
        on_delete=models.CASCADE,
        related_name='submission_outputs'
    )
    
    output = models.ForeignKey(
        'Output',
        on_delete=models.CASCADE,
        related_name='submission_inclusions'
    )
    
    order = models.IntegerField(
        default=0,
        help_text="Display order within submission"
    )
    
    submission_notes = models.TextField(
        blank=True,
        help_text="Notes specific to this output's inclusion in this submission"
    )
    
    is_reserve = models.BooleanField(
        default=False,
        help_text="Is this a reserve/backup output?"
    )
    
    strategic_importance = models.CharField(
        max_length=20,
        choices=[
            ('critical', 'Critical'),
            ('important', 'Important'),
            ('standard', 'Standard'),
            ('optional', 'Optional'),
        ],
        default='standard',
        help_text="Strategic importance of this output to the submission"
    )
    
    included_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'included_date']
        unique_together = ['submission', 'output']
        verbose_name = "Submission Output"
        verbose_name_plural = "Submission Outputs"
    
    def __str__(self):
        return f"{self.submission.name}: {self.output.title[:50]}"


# ============================================================
# USAGE NOTES:
# ============================================================
#
# 1. Add these models to your core/models.py
# 2. Run: python manage.py makemigrations core
# 3. Run: python manage.py migrate core
#
# Example usage:
#
# # Create a submission
# submission = REFSubmission.objects.create(
#     name="Main Submission 2029",
#     uoa="UOA 25 - Modern Languages",
#     submission_year=2029
# )
#
# # Add outputs
# output1 = Output.objects.get(id=1)
# output2 = Output.objects.get(id=2)
# 
# SubmissionOutput.objects.create(submission=submission, output=output1, order=1)
# SubmissionOutput.objects.create(submission=submission, output=output2, order=2)
#
# # Calculate metrics
# submission.calculate_all_metrics()
#
# # Get overall score
# score = submission.get_overall_portfolio_score()
#
# # Check readiness
# readiness = submission.get_submission_readiness()
#

# Access Control Models
from .models_access_control import Role, UserProfile, PanelAssignment, InternalRating
