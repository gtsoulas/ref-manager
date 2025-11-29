# Generated migration for three-component ratings
# Save as: core/migrations/0016_three_component_ratings.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_role_userprofile_panelassignment_internalrating'),
    ]

    operations = [
        # InternalPanelAssignment - Add three component ratings
        migrations.AddField(
            model_name='internalpanelassignment',
            name='originality_rating',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Rate originality from 0.00 to 4.00', 
                max_digits=3, 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='internalpanelassignment',
            name='significance_rating',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Rate significance from 0.00 to 4.00', 
                max_digits=3, 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='internalpanelassignment',
            name='rigour_rating',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Rate rigour from 0.00 to 4.00', 
                max_digits=3, 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='internalpanelassignment',
            name='component_average_rating',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Calculated average of O/S/R', 
                max_digits=3, 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='internalpanelassignment',
            name='confidential_comments',
            field=models.TextField(
                blank=True, 
                help_text='Confidential comments visible only to admins, observers, and panel members'
            ),
        ),
        
        # CriticalFriendAssignment - Add three component ratings
        migrations.AddField(
            model_name='criticalfriendassignment',
            name='originality_rating',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Rate originality from 0.00 to 4.00', 
                max_digits=3, 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='criticalfriendassignment',
            name='significance_rating',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Rate significance from 0.00 to 4.00', 
                max_digits=3, 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='criticalfriendassignment',
            name='rigour_rating',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Rate rigour from 0.00 to 4.00', 
                max_digits=3, 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='criticalfriendassignment',
            name='component_average_rating',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='Calculated average of O/S/R', 
                max_digits=3, 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='criticalfriendassignment',
            name='confidential_comments',
            field=models.TextField(
                blank=True, 
                help_text='Confidential comments visible only to admins and observers'
            ),
        ),
    ]
