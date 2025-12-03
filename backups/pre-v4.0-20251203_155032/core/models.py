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
    
    # ========== NEW: OPEN ACCESS STATUS CHOICES (from evaluation) ==========
    OA_STATUS_CHOICES = [
        ('gold', 'Gold Open Access (Journal-hosted, paid APC)'),
        ('green', 'Green Open Access (Repository, e.g., YORA)'),
        ('hybrid', 'Hybrid (Subscription journal + OA option)'),
        ('bronze', 'Bronze (Free to read, no formal license)'),
        ('closed', 'Closed / Paywalled'),
        ('non_compliant', 'Non-Compliant with REF OA Policy'),
    ]
    
    OA_EXCEPTION_CHOICES = [
        ('none', 'No Exception Required'),
        ('deposit', 'Deposit Exception (Technical/Personal barrier)'),
        ('access', 'Access Exception (Publisher embargo)'),
        ('technical', 'Technical Exception'),
        ('gold_route', 'Gold Route Exception'),
        ('other', 'Other (See compliance notes)'),
    ]
    # ========== END NEW CHOICES ==========
    
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
    
    # ========== NEW: O/S/R SELF-ASSESSMENT RATINGS ==========
    # REF 2029 three-component rating system for author self-assessment
    
    originality_self = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Originality (Self)",
        help_text="Self-assessment of originality (0.00-4.00)"
    )
    
    significance_self = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Significance (Self)",
        help_text="Self-assessment of significance (0.00-4.00)"
    )
    
    rigour_self = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Rigour (Self)",
        help_text="Self-assessment of rigour (0.00-4.00)"
    )
    
    # ========== O/S/R INTERNAL PANEL RATINGS ==========
    # For manually entering ratings received from internal panel members
    
    originality_internal = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Originality (Internal)",
        help_text="Internal panel assessment of originality (0.00-4.00)"
    )
    
    significance_internal = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Significance (Internal)",
        help_text="Internal panel assessment of significance (0.00-4.00)"
    )
    
    rigour_internal = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Rigour (Internal)",
        help_text="Internal panel assessment of rigour (0.00-4.00)"
    )
    
    # ========== O/S/R CRITICAL FRIEND RATINGS ==========
    # For manually entering ratings received from critical friends
    
    originality_external = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Originality (Critical Friend)",
        help_text="Critical friend assessment of originality (0.00-4.00)"
    )
    
    significance_external = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Significance (Critical Friend)",
        help_text="Critical friend assessment of significance (0.00-4.00)"
    )
    
    rigour_external = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Rigour (Critical Friend)",
        help_text="Critical friend assessment of rigour (0.00-4.00)"
    )
    
    @property
    def osr_self_average(self):
        """Calculate average of O/S/R self-assessment ratings."""
        ratings = [r for r in [self.originality_self, self.significance_self, self.rigour_self] if r is not None]
        if not ratings:
            return None
        return sum(ratings) / len(ratings)
    
    @property
    def osr_internal_average(self):
        """Calculate average of O/S/R internal panel ratings."""
        ratings = [r for r in [self.originality_internal, self.significance_internal, self.rigour_internal] if r is not None]
        if not ratings:
            return None
        return sum(ratings) / len(ratings)
    
    @property
    def osr_external_average(self):
        """Calculate average of O/S/R critical friend ratings."""
        ratings = [r for r in [self.originality_external, self.significance_external, self.rigour_external] if r is not None]
        if not ratings:
            return None
        return sum(ratings) / len(ratings)
    
    @property
    def osr_combined_average(self):
        """Calculate combined average across all O/S/R rating sources."""
        averages = [avg for avg in [self.osr_self_average, self.osr_internal_average, self.osr_external_average] if avg is not None]
        if not averages:
            return None
        return sum(averages) / len(averages)
    
    @property
    def osr_combined_average_no_self(self):
        """Calculate combined average excluding self-assessment (internal + external only)."""
        averages = [avg for avg in [self.osr_internal_average, self.osr_external_average] if avg is not None]
        if not averages:
            return None
        return sum(averages) / len(averages)
    
    # ========== O/S/R INTERNAL PANEL RATINGS ==========
    # For entering ratings received from internal panel members
    
    originality_internal = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Originality (Internal)",
        help_text="Internal panel rating for originality (0.00-4.00)"
    )
    
    significance_internal = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Significance (Internal)",
        help_text="Internal panel rating for significance (0.00-4.00)"
    )
    
    rigour_internal = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Rigour (Internal)",
        help_text="Internal panel rating for rigour (0.00-4.00)"
    )
    
    @property
    def osr_internal_average(self):
        """Calculate average of O/S/R internal panel ratings."""
        ratings = [r for r in [self.originality_internal, self.significance_internal, self.rigour_internal] if r is not None]
        if not ratings:
            return None
        return sum(ratings) / len(ratings)
    
    # ========== O/S/R CRITICAL FRIEND RATINGS ==========
    # For entering ratings received from critical friends/external reviewers
    
    originality_external = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Originality (External)",
        help_text="Critical friend rating for originality (0.00-4.00)"
    )
    
    significance_external = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Significance (External)",
        help_text="Critical friend rating for significance (0.00-4.00)"
    )
    
    rigour_external = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        verbose_name="Rigour (External)",
        help_text="Critical friend rating for rigour (0.00-4.00)"
    )
    
    @property
    def osr_external_average(self):
        """Calculate average of O/S/R critical friend ratings."""
        ratings = [r for r in [self.originality_external, self.significance_external, self.rigour_external] if r is not None]
        if not ratings:
            return None
        return sum(ratings) / len(ratings)
    
    @property
    def osr_combined_average(self):
        """Calculate combined average of all O/S/R ratings (internal, external, self)."""
        all_ratings = []
        for field in [self.originality_internal, self.significance_internal, self.rigour_internal,
                      self.originality_external, self.significance_external, self.rigour_external,
                      self.originality_self, self.significance_self, self.rigour_self]:
            if field is not None:
                all_ratings.append(field)
        if not all_ratings:
            return None
        return sum(all_ratings) / len(all_ratings)
    
    @property
    def osr_combined_average_no_self(self):
        """Calculate combined average of internal and external O/S/R ratings (excluding self)."""
        all_ratings = []
        for field in [self.originality_internal, self.significance_internal, self.rigour_internal,
                      self.originality_external, self.significance_external, self.rigour_external]:
            if field is not None:
                all_ratings.append(field)
        if not all_ratings:
            return None
        return sum(all_ratings) / len(all_ratings)
    
    is_double_weighted = models.BooleanField(default=False)
    is_interdisciplinary = models.BooleanField(default=False)
    is_open_access = models.BooleanField(default=False)
    
    # ========== NEW: REF COMPLIANCE FIELDS (from evaluation) ==========
    
    # OA Compliance Date Tracking
    acceptance_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Acceptance Date",
        help_text="Date paper was accepted for publication. Critical for 3-month deposit rule verification."
    )
    
    deposit_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Repository Deposit Date",
        help_text="Date uploaded to institutional repository (e.g., YORA)."
    )
    
    embargo_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Embargo End Date",
        help_text="Date when full-text access becomes publicly available."
    )
    
    # Detailed OA Status (supplements is_open_access boolean)
    oa_status = models.CharField(
        max_length=20,
        choices=OA_STATUS_CHOICES,
        default='closed',
        verbose_name="Open Access Status",
        help_text="Detailed Open Access status for REF compliance reporting."
    )
    
    oa_exception = models.CharField(
        max_length=20,
        choices=OA_EXCEPTION_CHOICES,
        default='none',
        verbose_name="OA Exception Type",
        help_text="Exception type if output does not meet standard OA requirements."
    )
    
    # REF Narrative Fields
    double_weighting_statement = models.TextField(
        blank=True,
        verbose_name="Double Weighting Statement",
        help_text="Required if Double Weighted. Max 300 words explaining why this output merits extended scope/scale weighting."
    )
    
    interdisciplinary_statement = models.TextField(
        blank=True,
        verbose_name="Interdisciplinary Statement",
        help_text="Explain the interdisciplinary methodology, contribution, and cross-panel value."
    )
    
    # Metrics
    citation_count = models.IntegerField(
        default=0,
        verbose_name="Citation Count",
        help_text="Citation count from OpenAlex/Crossref. Auto-updated on DOI fetch."
    )
    
    # ========== END NEW REF COMPLIANCE FIELDS ==========
    
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

    # ========== NEW: OA COMPLIANCE CHECK METHODS (from evaluation) ==========
    
    def check_oa_compliance(self):
        """
        Check if the output meets the REF Open Access 3-month deposit rule.
        
        Returns:
            tuple: (is_compliant: bool or None, message: str)
            - None indicates compliance cannot be determined (missing dates)
            - True indicates compliant
            - False indicates non-compliant
        """
        # If no acceptance date, we can't verify compliance
        if not self.acceptance_date:
            return (None, "Acceptance date required to verify compliance")
        
        # If no deposit date, definitely non-compliant (unless exception applies)
        if not self.deposit_date:
            if self.oa_exception != 'none':
                return (None, f"No deposit date, but exception applied: {self.get_oa_exception_display()}")
            return (False, "No repository deposit recorded")
        
        # Calculate days between acceptance and deposit
        delta = (self.deposit_date - self.acceptance_date).days
        
        if delta <= 92:  # Approximately 3 months
            return (True, f"Compliant: Deposited {delta} days after acceptance")
        else:
            if self.oa_exception != 'none':
                return (None, f"Late deposit ({delta} days), but exception: {self.get_oa_exception_display()}")
            return (False, f"Non-compliant: {delta} days exceeds 3-month rule (92 days)")

    def get_compliance_status_display(self):
        """
        Get a formatted compliance status for display in templates.
        
        Returns:
            str: Formatted status with icon
        """
        is_compliant, message = self.check_oa_compliance()
        
        if is_compliant is None:
            return f"⚪ {message}"
        elif is_compliant:
            return f"✅ {message}"
        else:
            return f"❌ {message}"

    def get_oa_status_badge(self):
        """
        Get Bootstrap badge HTML for OA status display.
        
        Returns:
            str: HTML badge string
        """
        badge_classes = {
            'gold': 'bg-warning text-dark',
            'green': 'bg-success',
            'hybrid': 'bg-info',
            'bronze': 'bg-secondary',
            'closed': 'bg-danger',
            'non_compliant': 'bg-dark',
        }
        
        badge_class = badge_classes.get(self.oa_status, 'bg-secondary')
        return f'<span class="badge {badge_class}">{self.get_oa_status_display()}</span>'

    def validate_double_weighting_statement(self):
        """
        Validate the double weighting statement meets requirements.
        
        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []
        
        if self.is_double_weighted and not self.double_weighting_statement:
            errors.append("Double-weighted outputs require a justification statement.")
        
        if self.double_weighting_statement:
            word_count = len(self.double_weighting_statement.split())
            if word_count > 300:
                errors.append(f"Statement has {word_count} words; maximum is 300.")
        
        return (len(errors) == 0, errors)

    # ========== END NEW OA COMPLIANCE METHODS ==========

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
        # Basic checks
        if not self.title or not self.all_authors:
            return False
        
        # Quality rating required
        if not self.quality_rating_average and not self.quality_rating:
            return False
        
        # OA compliance check (using new method)
        compliance_result = self.check_oa_compliance()
        if compliance_result[0] == False:  # Explicitly non-compliant
            return False
        
        # Status check
        if self.status not in ['approved', 'ready']:
            return False
        
        return True
    
    class Meta:
        ordering = ['-publication_year', 'title']
    
    def __str__(self):
        return f"{self.title[:50]} ({self.publication_year})"
    
    def get_absolute_url(self):
        return reverse('output_detail', kwargs={'pk': self.pk})


class CriticalFriend(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('limited', 'Limited Availability'),
        ('unavailable', 'Currently Unavailable'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField(validators=[EmailValidator()])
    institution = models.CharField(max_length=200)
    department = models.CharField(max_length=200, blank=True)
    
    expertise_areas = models.TextField(
        help_text="Research areas and expertise (comma-separated)"
    )
    research_interests = models.TextField(blank=True)
    
    phone = models.CharField(max_length=50, blank=True)
    orcid = models.CharField(max_length=50, blank=True)
    
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    max_assignments = models.IntegerField(
        default=5,
        help_text="Maximum concurrent review assignments"
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Critical Friend'
        verbose_name_plural = 'Critical Friends'
    
    def __str__(self):
        return f"{self.name} ({self.institution})"
    
    def get_absolute_url(self):
        return reverse('critical_friend_detail', kwargs={'pk': self.pk})
    
    @property
    def current_assignments_count(self):
        return self.assignments.filter(
            status__in=['assigned', 'accepted', 'in-progress']
        ).count()
    
    @property
    def can_accept_more(self):
        return self.current_assignments_count < self.max_assignments


class CriticalFriendAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
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
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='assigned'
    )
    
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Review fields
    quality_assessment = models.CharField(
        max_length=2,
        choices=QUALITY_CHOICES,
        blank=True
    )
    
    # Three-part rating fields
    originality_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        help_text="Originality rating (0.00-4.00)"
    )
    significance_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        help_text="Significance rating (0.00-4.00)"
    )
    rigour_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        help_text="Rigour rating (0.00-4.00)"
    )
    
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    overall_comments = models.TextField(blank=True)
    
    notes = models.TextField(blank=True, help_text="Internal notes")
    
    class Meta:
        ordering = ['-assigned_date']
        unique_together = ['output', 'critical_friend']
    
    def __str__(self):
        return f"{self.output.title[:30]} - {self.critical_friend.name}"
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now().date() > self.due_date
        return False
    
    def get_average_rating(self):
        """Calculate average of O/S/R ratings"""
        ratings = [r for r in [self.originality_rating, self.significance_rating, self.rigour_rating] if r is not None]
        if ratings:
            return sum(ratings) / len(ratings)
        return None


class Request(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    from_entity = models.CharField(max_length=200, help_text="Who is the request from?")
    subject = models.CharField(max_length=300)
    description = models.TextField()
    
    deadline = models.DateField(null=True, blank=True)
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
        related_name='assigned_requests'
    )
    
    response = models.TextField(blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} (from {self.from_entity})"
    
    @property
    def is_overdue(self):
        if self.deadline and self.status not in ['completed', 'cancelled']:
            return timezone.now().date() > self.deadline
        return False


class InternalReview(models.Model):
    """Internal review by department staff before external review"""
    
    QUALITY_CHOICES = Output.QUALITY_CHOICES
    
    output = models.ForeignKey(
        Output,
        on_delete=models.CASCADE,
        related_name='internal_reviews'
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    
    quality_assessment = models.CharField(
        max_length=2,
        choices=QUALITY_CHOICES,
        blank=True
    )
    comments = models.TextField()
    recommendations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['output', 'reviewer']
    
    def __str__(self):
        return f"Review of {self.output.title[:30]} by {self.reviewer.get_full_name()}"


class InternalPanelMember(models.Model):
    """Internal panel member model"""
    ROLE_CHOICES = [
        ('chair', 'Panel Chair'),
        ('deputy', 'Deputy Chair'),
        ('member', 'Panel Member'),
        ('observer', 'Observer'),
    ]
    
    colleague = models.ForeignKey(
        Colleague,
        on_delete=models.CASCADE,
        related_name='panel_memberships'
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    expertise_area = models.CharField(max_length=200, blank=True)
    appointed_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['colleague__user__last_name']
        verbose_name = 'Internal Panel Member'
        verbose_name_plural = 'Internal Panel Members'
    
    def __str__(self):
        return f"{self.colleague.user.get_full_name()} ({self.get_role_display()})"
    
    @property
    def current_assignments_count(self):
        return self.panel_assignments.filter(
            status__in=['assigned', 'in_progress']
        ).count()


class InternalPanelAssignment(models.Model):
    """Assignment of output to internal panel member for review"""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('deferred', 'Deferred'),
    ]
    
    REVIEWER_TYPE_CHOICES = [
        ('lead', 'Lead Reviewer'),
        ('second', 'Second Reviewer'),
        ('specialist', 'Specialist'),
        ('general', 'General Reviewer'),
    ]
    
    QUALITY_CHOICES = Output.QUALITY_CHOICES
    
    output = models.ForeignKey(
        Output,
        on_delete=models.CASCADE,
        related_name='internal_panel_assignments'
    )
    panel_member = models.ForeignKey(
        InternalPanelMember,
        on_delete=models.CASCADE,
        related_name='panel_assignments'
    )
    
    reviewer_type = models.CharField(
        max_length=20,
        choices=REVIEWER_TYPE_CHOICES,
        default='general',
        help_text="Classification of reviewer expertise for this output"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    assigned_date = models.DateField(auto_now_add=True)
    review_date = models.DateField(null=True, blank=True)
    
    rating_recommendation = models.CharField(
        max_length=2,
        choices=QUALITY_CHOICES,
        blank=True,
        help_text="Recommended quality rating"
    )
    
    # Three-part rating fields
    originality_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        help_text="Originality rating (0.00-4.00)"
    )
    significance_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        help_text="Significance rating (0.00-4.00)"
    )
    rigour_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        help_text="Rigour rating (0.00-4.00)"
    )
    
    comments = models.TextField(blank=True)
    confidential_comments = models.TextField(
        blank=True,
        help_text="Comments visible only to admin and other panel members"
    )
    
    class Meta:
        ordering = ['-assigned_date']
        unique_together = ['output', 'panel_member']
        verbose_name = 'Internal Panel Assignment'
        verbose_name_plural = 'Internal Panel Assignments'
    
    def __str__(self):
        return f"{self.output.title[:30]} - {self.panel_member}"
    
    def get_average_rating(self):
        """Calculate average of O/S/R ratings"""
        ratings = [r for r in [self.originality_rating, self.significance_rating, self.rigour_rating] if r is not None]
        if ratings:
            return sum(ratings) / len(ratings)
        return None


class Task(models.Model):
    """Task model for tracking REF management activities"""
    
    CATEGORY_CHOICES = [
        ('data_collection', 'Data Collection'),
        ('review', 'Output Review'),
        ('compliance', 'Compliance Check'),
        ('communication', 'Communication'),
        ('documentation', 'Documentation'),
        ('training', 'Training'),
        ('reporting', 'Reporting'),
        ('other', 'Other'),
    ]
    
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
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )
    
    class Meta:
        ordering = ['-priority', 'due_date', '-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now().date() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None


class REFSubmission(models.Model):
    """REF Submission tracking model"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('submitted', 'Submitted'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    uoa = models.CharField(max_length=100, verbose_name="Unit of Assessment")
    submission_year = models.IntegerField(
        validators=[MinValueValidator(2025), MaxValueValidator(2035)]
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    outputs = models.ManyToManyField(
        Output,
        through='SubmissionOutput',
        related_name='ref_submissions'
    )
    
    # Portfolio metrics
    portfolio_quality_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('4.00'))],
        help_text="Average quality score of included outputs (0-4 scale)"
    )
    
    portfolio_risk_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Average risk score of included outputs (0-1 scale)"
    )
    
    representativeness_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="How well outputs represent staff research (0-1 scale)"
    )
    
    equality_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="EDI metric for submission balance"
    )
    
    gender_balance_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Gender balance metric (0.5 = perfect balance)"
    )
    
    ecr_representation_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Early Career Researcher representation"
    )
    
    interdisciplinary_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        help_text="Proportion of interdisciplinary outputs"
    )
    
    # Weighting factors for portfolio optimization
    weight_quality = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.50'),
        help_text="Weight for quality in overall score"
    )
    
    weight_risk = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.20'),
        help_text="Weight for risk in overall score"
    )
    
    weight_representativeness = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.10'),
        help_text="Weight for representativeness"
    )
    
    weight_equality = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.10'),
        help_text="Weight for equality metrics"
    )
    
    weight_gender_balance = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.10'),
        help_text="Weight for gender balance"
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metrics_last_calculated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submission_year', 'name']
        verbose_name = 'REF Submission'
        verbose_name_plural = 'REF Submissions'
    
    def __str__(self):
        return f"{self.name} ({self.uoa}, {self.submission_year})"
    
    def calculate_quality_score(self):
        """Calculate average quality score from included outputs."""
        outputs = self.outputs.all()
        if not outputs:
            self.portfolio_quality_score = Decimal('0.00')
            return
        
        quality_map = {'4*': 4.0, '3*': 3.0, '2*': 2.0, '1*': 1.0, 'U': 0.0}
        total = 0
        count = 0
        
        for output in outputs:
            rating = output.quality_rating_average or output.quality_rating
            if rating:
                try:
                    total += float(rating)
                    count += 1
                except (ValueError, TypeError):
                    if rating in quality_map:
                        total += quality_map[rating]
                        count += 1
        
        if count > 0:
            self.portfolio_quality_score = Decimal(str(total / count))
        else:
            self.portfolio_quality_score = Decimal('0.00')
    
    def calculate_risk_score(self):
        """Calculate average risk score from included outputs."""
        outputs = self.outputs.all()
        if not outputs:
            self.portfolio_risk_score = Decimal('0.00')
            return
        
        total_risk = sum(float(o.overall_risk_score) for o in outputs)
        self.portfolio_risk_score = Decimal(str(total_risk / outputs.count()))
    
    def calculate_representativeness(self):
        """Calculate how well outputs represent the staff base."""
        from django.db.models import Count
        
        total_returnable = Colleague.objects.filter(
            is_returnable=True,
            employment_status='current'
        ).count()
        
        if total_returnable == 0:
            self.representativeness_score = Decimal('0.00')
            return
        
        colleagues_with_outputs = self.outputs.values('colleague').distinct().count()
        self.representativeness_score = Decimal(str(colleagues_with_outputs / total_returnable))
    
    def calculate_equality(self):
        """Calculate equality/diversity metrics."""
        # Placeholder - customize based on your EDI requirements
        self.equality_score = Decimal('50.00')
    
    def calculate_gender_balance(self):
        """Calculate gender balance of included outputs."""
        # Placeholder - would need gender field on Colleague model
        self.gender_balance_score = Decimal('0.50')
    
    def calculate_all_metrics(self):
        """Calculate all portfolio metrics."""
        self.calculate_quality_score()
        self.calculate_risk_score()
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
