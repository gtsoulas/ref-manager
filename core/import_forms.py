"""
Forms for importing data from CSV files
"""
from django import forms
from django.core.exceptions import ValidationError
import csv
import io


class CSVUploadForm(forms.Form):
    """Form for uploading CSV files"""
    csv_file = forms.FileField(
        label='Select CSV File',
        help_text='Upload a CSV file containing research output data',
        widget=forms.FileInput(attrs={
            'accept': '.csv',
            'class': 'form-control'
        })
    )
    
    skip_duplicates = forms.BooleanField(
        label='Skip duplicate outputs (based on title)',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    create_missing_staff = forms.BooleanField(
        label='Automatically create staff records for unknown authors',
        required=False,
        initial=True,
        help_text='If unchecked, outputs with unknown authors will be skipped',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_csv_file(self):
        """Validate the uploaded CSV file"""
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise ValidationError('File must be a CSV file (.csv)')
        
        if csv_file.size > 5 * 1024 * 1024:  # 5MB limit
            raise ValidationError('File size must be under 5MB')
        
        # Try to read the file to validate it's valid CSV
        try:
            csv_file.seek(0)
            content = csv_file.read().decode('utf-8')
            csv_file.seek(0)
            
            # Check if it has the required columns
            reader = csv.DictReader(io.StringIO(content))
            fieldnames = reader.fieldnames
            
            required_fields = ['Title', 'Person']
            missing_fields = [f for f in required_fields if f not in fieldnames]
            
            if missing_fields:
                raise ValidationError(
                    f'CSV file is missing required columns: {", ".join(missing_fields)}'
                )
                
        except UnicodeDecodeError:
            raise ValidationError('File must be UTF-8 encoded')
        except csv.Error as e:
            raise ValidationError(f'Invalid CSV file: {str(e)}')
        
        return csv_file
