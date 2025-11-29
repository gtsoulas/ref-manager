#!/usr/bin/env python3
"""
REF-Manager v3.1 Model Patcher
Safely patches models.py with three-component ratings

Run from ref-manager directory:
    python v3.1-upgrade/patch_models.py
"""

import os
import sys
import shutil
from datetime import datetime

def main():
    models_path = 'core/models.py'
    
    if not os.path.exists(models_path):
        print("❌ core/models.py not found. Run from ref-manager directory.")
        sys.exit(1)
    
    # Read current content
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if 'component_average_rating' in content:
        print("✓ Models already patched for v3.1")
        return
    
    # Backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'core/models.py.pre-v3.1.{timestamp}'
    shutil.copy(models_path, backup_path)
    print(f"✓ Backup created: {backup_path}")
    
    # ===========================================
    # PATCH 1: InternalPanelAssignment
    # Add new fields after "notes = models.TextField(blank=True)"
    # ===========================================
    
    internal_panel_marker = '    notes = models.TextField(blank=True)\n\n    class Meta:\n        verbose_name = \'Internal Panel Assignment\''
    
    internal_panel_new_fields = '''    notes = models.TextField(blank=True)

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

    class Meta:
        verbose_name = 'Internal Panel Assignment\''''
    
    if internal_panel_marker in content:
        content = content.replace(internal_panel_marker, internal_panel_new_fields)
        print("✓ Patched InternalPanelAssignment")
    else:
        print("⚠ Could not find InternalPanelAssignment marker - trying alternative...")
        # Try simpler marker
        simple_marker = '    notes = models.TextField(blank=True)\n\n    class Meta:'
        if simple_marker in content:
            new_simple = '''    notes = models.TextField(blank=True)

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

    class Meta:'''
            # Only replace the first occurrence (InternalPanelAssignment, not CriticalFriendAssignment)
            content = content.replace(simple_marker, new_simple, 1)
            print("✓ Patched InternalPanelAssignment (alternative method)")
        else:
            print("❌ Could not patch InternalPanelAssignment")
    
    # ===========================================
    # PATCH 2: CriticalFriendAssignment
    # Replace integer scores with decimal ratings
    # ===========================================
    
    # Old fields to replace
    old_cf_fields = '''    originality_score = models.IntegerField(
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
    
    internal_notes = models.TextField(blank=True)'''
    
    new_cf_fields = '''    # Three-component ratings (v3.1 - decimal scale 0.00-4.00)
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
        return None'''
    
    if old_cf_fields in content:
        content = content.replace(old_cf_fields, new_cf_fields)
        print("✓ Patched CriticalFriendAssignment")
    else:
        print("⚠ Could not find exact CriticalFriendAssignment fields")
        print("  You may need to patch manually - see MODELS_PATCH.py")
    
    # Write patched content
    with open(models_path, 'w') as f:
        f.write(content)
    
    print("")
    print("✓ models.py patched successfully")
    print("")
    print("Next steps:")
    print("  python manage.py makemigrations")
    print("  python manage.py migrate")


if __name__ == '__main__':
    main()
