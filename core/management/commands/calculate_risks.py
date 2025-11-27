# ============================================================
# FILE: core/management/commands/calculate_risks.py
# Management command to calculate/recalculate risk scores
# ============================================================

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Avg
from core.models import Output, REFSubmission
from decimal import Decimal


class Command(BaseCommand):
    help = 'Calculate or recalculate risk scores for all outputs and submissions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-timeline',
            action='store_true',
            help='Automatically set timeline risk from publication status',
        )
        
        parser.add_argument(
            '--outputs-only',
            action='store_true',
            help='Only update output risks, skip submissions',
        )
        
        parser.add_argument(
            '--submissions-only',
            action='store_true',
            help='Only update submission metrics, skip outputs',
        )
        
        parser.add_argument(
            '--output-id',
            type=int,
            help='Calculate risk for a specific output ID',
        )
        
        parser.add_argument(
            '--submission-id',
            type=int,
            help='Calculate metrics for a specific submission ID',
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Print detailed progress information',
        )
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        
        # Calculate output risks
        if not options['submissions_only']:
            if options['output_id']:
                # Single output
                self.update_single_output(options['output_id'], options['auto_timeline'], verbose)
            else:
                # All outputs
                self.update_all_outputs(options['auto_timeline'], verbose)
        
        # Calculate submission metrics
        if not options['outputs_only']:
            if options['submission_id']:
                # Single submission
                self.update_single_submission(options['submission_id'], verbose)
            else:
                # All submissions
                self.update_all_submissions(verbose)
        
        self.stdout.write(self.style.SUCCESS('\n✓ Risk calculation complete!'))
    
    def update_single_output(self, output_id, auto_timeline, verbose):
        """Update risk for a single output"""
        try:
            output = Output.objects.get(id=output_id)
            
            if auto_timeline:
                output.auto_set_timeline_risk()
                if verbose:
                    self.stdout.write(f'  Timeline risk set to {output.timeline_risk_score}')
            
            output.calculate_overall_risk()
            output.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Updated output #{output_id}: "{output.title[:50]}" '
                    f'(Risk: {output.overall_risk_score})'
                )
            )
        except Output.DoesNotExist:
            raise CommandError(f'Output with ID {output_id} does not exist')
    
    def update_all_outputs(self, auto_timeline, verbose):
        """Update risks for all outputs"""
        self.stdout.write('Calculating output risks...')
        
        outputs = Output.objects.all()
        total = outputs.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('  No outputs found'))
            return
        
        updated = 0
        errors = 0
        
        for i, output in enumerate(outputs, 1):
            try:
                if auto_timeline:
                    output.auto_set_timeline_risk()
                
                old_risk = output.overall_risk_score
                output.calculate_overall_risk()
                output.save()
                
                updated += 1
                
                if verbose:
                    change = output.overall_risk_score - old_risk
                    change_str = f"({change:+.2f})" if change != 0 else ""
                    self.stdout.write(
                        f'  [{i}/{total}] {output.title[:40]}: '
                        f'{output.overall_risk_score:.2f} {change_str}'
                    )
                elif i % 10 == 0:
                    self.stdout.write(f'  Progress: {i}/{total} outputs processed')
                
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'  Error updating output #{output.id}: {str(e)}')
                )
        
        # Summary statistics
        avg_risk = outputs.aggregate(Avg('overall_risk_score'))['overall_risk_score__avg']
        high_risk = outputs.filter(overall_risk_score__gte=Decimal('0.75')).count()
        low_risk = outputs.filter(overall_risk_score__lt=Decimal('0.25')).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Updated {updated} outputs'
            )
        )
        
        if errors > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠ {errors} errors encountered')
            )
        
        self.stdout.write(f'\nRisk Statistics:')
        self.stdout.write(f'  Average risk: {avg_risk:.2f}')
        self.stdout.write(f'  High risk (≥0.75): {high_risk} ({high_risk/total*100:.1f}%)')
        self.stdout.write(f'  Low risk (<0.25): {low_risk} ({low_risk/total*100:.1f}%)')
    
    def update_single_submission(self, submission_id, verbose):
        """Update metrics for a single submission"""
        try:
            submission = REFSubmission.objects.get(id=submission_id)
            
            old_quality = submission.portfolio_quality_score
            old_risk = submission.portfolio_risk_score
            
            submission.calculate_all_metrics()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Updated submission #{submission_id}: "{submission.name}"'
                )
            )
            
            if verbose:
                self.stdout.write(f'  Quality: {old_quality:.2f} → {submission.portfolio_quality_score:.2f}')
                self.stdout.write(f'  Risk: {old_risk:.2f} → {submission.portfolio_risk_score:.2f}')
                self.stdout.write(f'  Overall score: {submission.get_overall_portfolio_score():.2f}')
                
        except REFSubmission.DoesNotExist:
            raise CommandError(f'Submission with ID {submission_id} does not exist')
    
    def update_all_submissions(self, verbose):
        """Update metrics for all submissions"""
        self.stdout.write('\nCalculating submission metrics...')
        
        submissions = REFSubmission.objects.all()
        total = submissions.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('  No submissions found'))
            return
        
        updated = 0
        errors = 0
        
        for i, submission in enumerate(submissions, 1):
            try:
                submission.calculate_all_metrics()
                updated += 1
                
                if verbose:
                    self.stdout.write(
                        f'  [{i}/{total}] {submission.name}: '
                        f'Quality={submission.portfolio_quality_score:.2f}, '
                        f'Risk={submission.portfolio_risk_score:.2f}, '
                        f'Score={submission.get_overall_portfolio_score():.2f}'
                    )
                
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'  Error updating submission #{submission.id}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Updated {updated} submissions')
        )
        
        if errors > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠ {errors} errors encountered')
            )


# ============================================================
# USAGE EXAMPLES:
# ============================================================
#
# Calculate risks for all outputs and submissions:
#   python manage.py calculate_risks
#
# Auto-set timeline risks based on publication status:
#   python manage.py calculate_risks --auto-timeline
#
# Update only outputs:
#   python manage.py calculate_risks --outputs-only
#
# Update only submissions:
#   python manage.py calculate_risks --submissions-only
#
# Update specific output:
#   python manage.py calculate_risks --output-id 42
#
# Update specific submission:
#   python manage.py calculate_risks --submission-id 5
#
# Verbose output:
#   python manage.py calculate_risks --verbose
#
# Combined options:
#   python manage.py calculate_risks --auto-timeline --verbose
#
