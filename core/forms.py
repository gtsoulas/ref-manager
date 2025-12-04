from django import forms
from django.core.exceptions import ValidationError
from .models import Task
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Colleague, Output, CriticalFriend, CriticalFriendAssignment,
    Request, InternalReview, InternalPanelMember, InternalPanelAssignment,
    OutputColleague
)

class ColleagueForm(forms.ModelForm):
    """Form for creating/editing colleague"""
    
    # User fields
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    username = forms.CharField(max_length=150, help_text="For login")
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Leave blank to keep existing password"
    )
    
    class Meta:
        model = Colleague
        fields = [
            'staff_id', 'title', 'fte', 'contract_type',
            'employment_status', 'employment_end_date',  # NEW FIELDS
            'unit_of_assessment', 'is_returnable', 'submission_group',
            'office', 'phone', 'notes'
        ]
        widgets = {
            'fte': forms.NumberInput(attrs={'step': '0.1', 'min': '0.1', 'max': '1.0'}),
            'employment_end_date': forms.DateInput(attrs={'type': 'date'}),  # NEW WIDGET
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate user fields if editing
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['username'].initial = user.username
            self.fields['password'].required = False
    
    def save(self, commit=True):
        colleague = super().save(commit=False)
        
        # Create or update user
        if colleague.pk:
            # Update existing user
            user = colleague.user
        else:
            # Create new user
            user = User()
            user.username = self.cleaned_data['username']
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        # Update password if provided
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
            colleague.user = user
            colleague.save()
        
        return colleague


class OutputForm(forms.ModelForm):
    """Form for creating/editing outputs - Enhanced with REF compliance fields"""
    
    # BibTeX import field
    bibtex_entry = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 8,
            'placeholder': 'Paste BibTeX entry here to auto-populate fields...',
            'class': 'form-control font-monospace'
        }),
        label="Import from BibTeX",
        help_text="Optional: Paste a BibTeX entry to automatically populate the form fields"
    )
    
    # NEW: Multiple colleague association fields
    associated_colleagues = forms.ModelMultipleChoiceField(
        queryset=Colleague.objects.none(),  # Set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label="Associated Colleagues",
        help_text="Select all colleagues associated with this output (e.g., co-authors from the department)"
    )
    
    main_colleague_id = forms.ChoiceField(
        choices=[],  # Populated dynamically in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Main Colleague (for REF)",
        help_text="Select the primary colleague for REF submission purposes. Must be one of the associated colleagues."
    )

    class Meta:
        model = Output
        fields = [
            # Basic Information
            'colleague', 'title', 'publication_type', 'publication_year',
            'publication_venue', 'volume', 'issue', 'pages',
            'doi', 'isbn', 'url', 'all_authors', 'author_position',
            'uoa', 'status', 
            
            # O/S/R Self-Assessment Ratings (REF 2029)
            'originality_self', 'significance_self', 'rigour_self',
            
            # O/S/R Internal Panel Ratings
            'originality_internal', 'significance_internal', 'rigour_internal',
            
            # O/S/R Critical Friend Ratings
            'originality_external', 'significance_external', 'rigour_external',
            
            # REF Flags
            'is_double_weighted', 'is_interdisciplinary', 'is_open_access',
            
            # REF Compliance Fields
            'oa_status',
            'oa_exception',
            'acceptance_date',
            'deposit_date',
            'embargo_end_date',
            'double_weighting_statement',
            'interdisciplinary_statement',
            'citation_count',
            'oa_compliance_notes',
            
            # Files
            'pdf_file', 'supplementary_file',
            
            # Additional Info
            'abstract', 'keywords', 'internal_notes'
        ]
        widgets = {
            'publication_year': forms.NumberInput(attrs={
                'min': '2021',
                'max': '2028',
                'placeholder': 'YYYY'
            }),
            'all_authors': forms.Textarea(attrs={'rows': 3}),
            'abstract': forms.Textarea(attrs={'rows': 4}),
            'keywords': forms.Textarea(attrs={'rows': 2}),
            'internal_notes': forms.Textarea(attrs={'rows': 3}),
            
            # O/S/R Self-Assessment widgets
            'originality_self': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'max': '4',
                'class': 'form-control',
                'placeholder': '0.00-4.00'
            }),
            'significance_self': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'max': '4',
                'class': 'form-control',
                'placeholder': '0.00-4.00'
            }),
            'rigour_self': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'max': '4',
                'class': 'form-control',
                'placeholder': '0.00-4.00'
            }),
            
            # O/S/R Internal Panel widgets
            'originality_internal': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'max': '4',
                'class': 'form-control',
                'placeholder': '0.00-4.00'
            }),
            'significance_internal': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'max': '4',
                'class': 'form-control',
                'placeholder': '0.00-4.00'
            }),
            'rigour_internal': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'max': '4',
                'class': 'form-control',
                'placeholder': '0.00-4.00'
            }),
            
            # O/S/R Critical Friend widgets
            'originality_external': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'max': '4',
                'class': 'form-control',
                'placeholder': '0.00-4.00'
            }),
            'significance_external': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'max': '4',
                'class': 'form-control',
                'placeholder': '0.00-4.00'
            }),
            'rigour_external': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0', 
                'max': '4',
                'class': 'form-control',
                'placeholder': '0.00-4.00'
            }),
            
            # NEW: Date fields with date picker
            'acceptance_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'deposit_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'embargo_end_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            
            # NEW: Narrative statement fields
            'double_weighting_statement': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Explain why this output merits double weighting. '
                               'Describe the extended scope, scale, or significance '
                               'that justifies counting as 2 outputs. (Max 300 words)',
            }),
            'interdisciplinary_statement': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Describe the interdisciplinary nature of this output. '
                               'Explain the methodology, contribution to multiple fields, '
                               'and cross-panel value.',
            }),
            
            # NEW: OA compliance notes
            'oa_compliance_notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Notes about OA compliance, exceptions, or issues...',
            }),
            
            # NEW: Citation count (display as readonly - updated via DOI fetch)
            'citation_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'title': 'Auto-updated when fetching DOI metadata',
                'style': 'background-color: #f8f9fa;',
            }),
        }
        
        help_texts = {
            'acceptance_date': 'Date the manuscript was accepted. Required to verify 3-month deposit rule.',
            'deposit_date': 'Date uploaded to institutional repository (e.g., YORA).',
            'embargo_end_date': 'Date when full-text access becomes available (if embargoed).',
            'oa_status': 'Detailed Open Access status for REF compliance tracking.',
            'oa_exception': 'Select exception type if output cannot meet standard OA requirements.',
            'double_weighting_statement': 'Required for double-weighted outputs. Maximum 300 words.',
            'interdisciplinary_statement': 'Describe cross-disciplinary methodology and value.',
            'citation_count': 'Citation count from OpenAlex. Auto-updates on DOI fetch.',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is not admin, hide colleague field (will be set automatically)
        if self.user and not (self.user.is_staff or self.user.groups.filter(name='Department Admin').exists()):
            self.fields['colleague'].widget = forms.HiddenInput()
            try:
                colleague = Colleague.objects.get(user=self.user)
                self.fields['colleague'].initial = colleague
            except Colleague.DoesNotExist:
                pass
        
        # NEW: Set up associated_colleagues queryset
        self.fields['associated_colleagues'].queryset = Colleague.objects.select_related(
            'user'
        ).filter(
            employment_status='current'
        ).order_by('user__last_name', 'user__first_name')
        
        # NEW: Build choices for main_colleague_id
        colleague_choices = [('', '-- Select main colleague --')]
        for c in self.fields['associated_colleagues'].queryset:
            colleague_choices.append((str(c.pk), c.user.get_full_name()))
        self.fields['main_colleague_id'].choices = colleague_choices
        
        # NEW: Pre-populate associated colleagues and main colleague when editing
        if self.instance and self.instance.pk:
            # Get current associations
            current_associations = OutputColleague.objects.filter(
                output=self.instance
            ).select_related('colleague')
            
            # Set initial associated colleagues
            associated_ids = [oc.colleague_id for oc in current_associations]
            # Also include the legacy colleague FK if not already in associations
            if self.instance.colleague_id and self.instance.colleague_id not in associated_ids:
                associated_ids.append(self.instance.colleague_id)
            self.fields['associated_colleagues'].initial = associated_ids
            
            # Set initial main colleague
            main_association = current_associations.filter(is_main=True).first()
            if main_association:
                self.fields['main_colleague_id'].initial = str(main_association.colleague_id)
            elif self.instance.colleague_id:
                # Fall back to legacy colleague FK
                self.fields['main_colleague_id'].initial = str(self.instance.colleague_id)
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.HiddenInput):
                existing_class = field.widget.attrs.get('class', '')
                if 'form-control' not in existing_class and not isinstance(field.widget, forms.CheckboxSelectMultiple):
                    field.widget.attrs['class'] = f'{existing_class} form-control'.strip()
        
        # Mark citation_count as visually distinct
        if 'citation_count' in self.fields:
            self.fields['citation_count'].widget.attrs['style'] = 'background-color: #f8f9fa;'
    
    def clean_double_weighting_statement(self):
        """
        Validate double weighting statement:
        - Required if is_double_weighted is True
        - Maximum 300 words
        """
        statement = self.cleaned_data.get('double_weighting_statement', '').strip()
        is_double = self.cleaned_data.get('is_double_weighted', False)
        
        if is_double and not statement:
            raise ValidationError(
                "A justification statement is required for double-weighted outputs. "
                "Please explain why this output merits double weighting."
            )
        
        if statement:
            word_count = len(statement.split())
            if word_count > 300:
                raise ValidationError(
                    f"Statement exceeds maximum length: {word_count} words. "
                    f"Please reduce to 300 words or fewer."
                )
        
        return statement
    
    def clean_interdisciplinary_statement(self):
        """
        Validate interdisciplinary statement.
        """
        statement = self.cleaned_data.get('interdisciplinary_statement', '').strip()
        
        if statement:
            word_count = len(statement.split())
            if word_count > 500:  # More generous limit for interdisciplinary
                raise ValidationError(
                    f"Statement too long: {word_count} words. "
                    f"Please reduce to 500 words or fewer."
                )
        
        return statement
    
    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        
        # Validate deposit date is after acceptance date
        acceptance_date = cleaned_data.get('acceptance_date')
        deposit_date = cleaned_data.get('deposit_date')
        
        if acceptance_date and deposit_date:
            if deposit_date < acceptance_date:
                self.add_error(
                    'deposit_date',
                    'Deposit date cannot be before acceptance date.'
                )
        
        # Validate embargo end date is after deposit date
        embargo_end = cleaned_data.get('embargo_end_date')
        if deposit_date and embargo_end:
            if embargo_end < deposit_date:
                self.add_error(
                    'embargo_end_date',
                    'Embargo end date should be after deposit date.'
                )
        
        # NEW: Validate main_colleague is in associated_colleagues
        main_colleague_id = cleaned_data.get('main_colleague_id')
        associated_colleagues = cleaned_data.get('associated_colleagues', [])
        
        if main_colleague_id:
            associated_ids = [str(c.pk) for c in associated_colleagues]
            if main_colleague_id not in associated_ids:
                self.add_error(
                    'main_colleague_id',
                    'Main colleague must be one of the associated colleagues.'
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Override save to handle colleague associations."""
        output = super().save(commit=False)
        
        if commit:
            output.save()
            self.save_m2m()  # Save standard M2M fields
            
            # Handle colleague associations
            associated_colleagues = self.cleaned_data.get('associated_colleagues', [])
            main_colleague_id = self.cleaned_data.get('main_colleague_id')
            
            if associated_colleagues:
                # Get existing associations
                existing_associations = {
                    oc.colleague_id: oc 
                    for oc in OutputColleague.objects.filter(output=output)
                }
                
                # Track which colleagues should be associated
                new_colleague_ids = set(c.pk for c in associated_colleagues)
                
                # Remove associations that are no longer needed
                for colleague_id in list(existing_associations.keys()):
                    if colleague_id not in new_colleague_ids:
                        existing_associations[colleague_id].delete()
                
                # Add or update associations
                for position, colleague in enumerate(associated_colleagues, start=1):
                    is_main = main_colleague_id and str(colleague.pk) == main_colleague_id
                    
                    if colleague.pk in existing_associations:
                        # Update existing
                        oc = existing_associations[colleague.pk]
                        oc.is_main = is_main
                        oc.author_position = position
                        oc.save()
                    else:
                        # Create new
                        OutputColleague.objects.create(
                            output=output,
                            colleague=colleague,
                            is_main=is_main,
                            author_position=position
                        )
                
                # Update the legacy colleague FK to the main colleague
                if main_colleague_id:
                    try:
                        output.colleague_id = int(main_colleague_id)
                        output.save(update_fields=['colleague_id'])
                    except (ValueError, TypeError):
                        pass
        
        return output


class OutputFilterForm(forms.Form):
    """Form for filtering outputs"""
    
    status = forms.ChoiceField(
        choices=[('', 'All')] + Output.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    quality_rating = forms.ChoiceField(
        choices=[('', 'All')] + Output.QUALITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # NEW: OA Status filter
    oa_status = forms.ChoiceField(
        choices=[('', 'All')] + Output.OA_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="OA Status"
    )
    
    uoa = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by UoA'
        })
    )
    
    colleague = forms.ModelChoiceField(
        queryset=Colleague.objects.select_related('user').all(),
        required=False,
        empty_label='All colleagues',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CriticalFriendForm(forms.ModelForm):
    """Form for creating/editing critical friends"""
    
    class Meta:
        model = CriticalFriend
        fields = [
            'name', 'email', 'institution', 'department',
            'expertise_areas', 'research_interests',
            'phone', 'orcid',
            'availability', 'max_assignments',
            'notes'
        ]
        widgets = {
            'expertise_areas': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'e.g., Machine Learning, Computer Vision, Natural Language Processing'
            }),
            'research_interests': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class AssignmentForm(forms.ModelForm):
    """Form for assigning output to critical friend"""
    
    class Meta:
        model = CriticalFriendAssignment
        fields = ['critical_friend', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'critical_friend': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only show available critical friends
        self.fields['critical_friend'].queryset = CriticalFriend.objects.filter(
            availability__in=['available', 'limited']
        )
        
        # Add helpful text
        self.fields['critical_friend'].help_text = 'Only showing available reviewers'


class ReviewResponseForm(forms.ModelForm):
    """Form for critical friends to submit their review"""
    
    class Meta:
        model = CriticalFriendAssignment
        fields = [
            'quality_assessment', 'originality_rating', 'significance_rating', 'rigour_rating',
            'strengths', 'weaknesses', 'suggestions', 'overall_comments'
        ]
        widgets = {
            'quality_assessment': forms.Select(attrs={'class': 'form-control'}),
            'originality_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '4'
            }),
            'significance_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '4'
            }),
            'rigour_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '4'
            }),
            'strengths': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'weaknesses': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'suggestions': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'overall_comments': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        from django.utils import timezone
        assignment = super().save(commit=False)
        assignment.status = 'completed'
        assignment.completed_date = timezone.now()
        
        if commit:
            assignment.save()
        
        return assignment


class RequestForm(forms.ModelForm):
    """Form for creating/editing requests"""
    
    class Meta:
        model = Request
        fields = [
            'from_entity', 'subject', 'description',
            'deadline', 'priority', 'status',
            'assigned_to', 'response'
        ]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'response': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'from_entity': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }


class InternalReviewForm(forms.ModelForm):
    """Form for internal reviews"""
    
    class Meta:
        model = InternalReview
        fields = ['quality_assessment', 'comments', 'recommendations']
        widgets = {
            'quality_assessment': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'recommendations': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class BulkUploadForm(forms.Form):
    """Form for bulk uploading outputs from CSV"""
    
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with output data',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    
    colleague = forms.ModelChoiceField(
        queryset=Colleague.objects.select_related('user').all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Select the colleague for these outputs'
    )


# NEW: Enhanced Bulk Import Form (from evaluation)
class EnhancedBulkImportForm(forms.Form):
    """
    Form for bulk importing outputs from CSV with OpenAlex integration.
    """
    
    csv_file = forms.FileField(
        label="Upload CSV File",
        help_text="CSV must have 'doi' column for smart import. "
                  "Include 'title', 'venue', 'year' for manual entries (book chapters).",
        widget=forms.FileInput(
            attrs={
                'accept': '.csv',
                'class': 'form-control',
            }
        )
    )
    
    IMPORT_MODE_CHOICES = [
        ('hybrid', 'Hybrid (Recommended) - Fetch DOI metadata if available, else use CSV'),
        ('smart', 'Smart Only - Fetch all metadata from DOIs (skips rows without DOI)'),
        ('manual', 'Manual Only - Use CSV data directly (no API calls)'),
    ]
    
    import_mode = forms.ChoiceField(
        choices=IMPORT_MODE_CHOICES,
        initial='hybrid',
        label="Import Mode",
        help_text="Hybrid mode handles both journal articles (with DOI) and book chapters (without DOI).",
        widget=forms.RadioSelect(
            attrs={'class': 'form-check-input'}
        )
    )
    
    skip_duplicates = forms.BooleanField(
        initial=True,
        required=False,
        label="Skip Duplicates",
        help_text="Skip rows where DOI or exact Title already exists in database.",
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )
    )
    
    auto_link_colleagues = forms.BooleanField(
        initial=True,
        required=False,
        label="Auto-link Colleagues",
        help_text="If CSV has 'staff_id' column, automatically link outputs to colleagues.",
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )
    )
    
    default_oa_status = forms.ChoiceField(
        choices=[('', '-- Use API data or leave blank --')] + list(Output.OA_STATUS_CHOICES),
        required=False,
        label="Default OA Status",
        help_text="Override OA status for all imports (useful for known repository deposits).",
        widget=forms.Select(
            attrs={'class': 'form-select'}
        )
    )


class InternalPanelMemberForm(forms.ModelForm):
    """Form for creating/editing internal panel members - shows only current employees"""
    
    class Meta:
        model = InternalPanelMember
        fields = ['colleague', 'role', 'expertise_area', 'appointed_date', 'is_active', 'notes']
        widgets = {
            'appointed_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # FILTER: Show only current employees
        self.fields['colleague'].queryset = Colleague.objects.filter(
            employment_status='current'
        ).select_related('user').order_by('user__last_name', 'user__first_name')
        
        # Label: Name + UoA
        self.fields['colleague'].label_from_instance = lambda obj: (
            f"{obj.user.get_full_name()} - {obj.unit_of_assessment}" if obj.unit_of_assessment 
            else obj.user.get_full_name()
        )
        
        # Make the dropdown more user-friendly


class InternalPanelAssignmentForm(forms.ModelForm):
    class Meta:
        model = InternalPanelAssignment
        fields = [
            'panel_member',
            'reviewer_type',  # NEW: Specialist classification
            'status', 
            'rating_recommendation',
            'originality_rating',
            'significance_rating',
            'rigour_rating',
            'confidential_comments',            
            'comments'
        ]
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
            'confidential_comments': forms.Textarea(attrs={'rows': 3}),
            'originality_rating': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '4'}),
            'significance_rating': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '4'}),
            'rigour_rating': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '4'}),
        }

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to show only active panel members (who are current employees)
        self.fields['panel_member'].queryset = InternalPanelMember.objects.filter(
            is_active=True,
            colleague__employment_status='current'
        ).select_related('colleague__user').order_by('colleague__user__last_name')
        
        # Make the dropdown more user-friendly
        self.fields['panel_member'].label_from_instance = lambda obj: f"{obj.colleague.user.get_full_name()} - {obj.get_role_display()}"        


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'category',
            'priority',
            'status',
            'assigned_to',
            'start_date',
            'due_date',
            'notes',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter task description'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes or updates'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        
        if start_date and due_date and start_date > due_date:
            raise forms.ValidationError(
                'Start date cannot be after due date.'
            )
        
        return cleaned_data
