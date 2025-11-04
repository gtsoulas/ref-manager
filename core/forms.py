from django import forms
from .models import Task
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Colleague, Output, CriticalFriend, CriticalFriendAssignment,
    Request, InternalReview, InternalPanelMember, InternalPanelAssignment
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
    """Form for creating/editing outputs"""
    
    class Meta:
        model = Output
        fields = [
            'colleague', 'title', 'publication_type', 'publication_date',
            'publication_venue', 'volume', 'issue', 'pages',
            'doi', 'isbn', 'url', 'all_authors', 'author_position',
            'uoa', 'status', 'quality_rating',
            'is_double_weighted', 'is_interdisciplinary', 'is_open_access',
            'pdf_file', 'supplementary_file',
            'abstract', 'keywords', 'internal_notes'
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'all_authors': forms.Textarea(attrs={'rows': 3}),
            'abstract': forms.Textarea(attrs={'rows': 4}),
            'keywords': forms.Textarea(attrs={'rows': 2}),
            'internal_notes': forms.Textarea(attrs={'rows': 3}),
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
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


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
            'quality_assessment', 'originality_score', 'significance_score', 'rigour_score',
            'strengths', 'weaknesses', 'suggestions', 'overall_comments'
        ]
        widgets = {
            'quality_assessment': forms.Select(attrs={'class': 'form-control'}),
            'originality_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'significance_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'rigour_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'strengths': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'weaknesses': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'suggestions': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'overall_comments': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }
    
    def save(self, commit=True):
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
        self.fields['colleague'].label_from_instance = lambda obj: f"{obj.user.get_full_name()} ({obj.department})"

class InternalPanelAssignmentForm(forms.ModelForm):
    class Meta:
        model = InternalPanelAssignment
        fields = ['panel_member', 'assigned_date', 'status', 'rating_recommendation', 'comments']
        widgets = {
            'assigned_date': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 4}),
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


