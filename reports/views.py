from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .latex_generator import LaTeXGenerator


@login_required
def reports_home(request):
    """Reports home page"""
    return render(request, 'reports/home.html')


@login_required
def submission_overview_report(request):
    """Generate submission overview report"""
    doc_class = request.GET.get('format', 'article')  # article, report, or beamer
    
    generator = LaTeXGenerator(document_class=doc_class)
    latex_source = generator.generate_submission_overview()
    
    # Return as downloadable .tex file
    response = HttpResponse(latex_source, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="submission_overview.tex"'
    return response


@login_required
def quality_profile_report(request):
    """Generate quality profile report"""
    doc_class = request.GET.get('format', 'article')
    
    generator = LaTeXGenerator(document_class=doc_class)
    latex_source = generator.generate_quality_profile()
    
    response = HttpResponse(latex_source, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="quality_profile.tex"'
    return response


@login_required
def staff_progress_report(request):
    """Generate staff progress report"""
    doc_class = request.GET.get('format', 'article')
    
    generator = LaTeXGenerator(document_class=doc_class)
    latex_source = generator.generate_staff_progress()
    
    response = HttpResponse(latex_source, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="staff_progress.tex"'
    return response


@login_required
def review_status_report(request):
    """Generate review status report"""
    doc_class = request.GET.get('format', 'article')
    
    generator = LaTeXGenerator(document_class=doc_class)
    
    # Simple report for now
    latex_source = r"""\documentclass{article}
\begin{document}
\title{Review Status Report}
\maketitle
\section{Review Status}
Coming soon - review status tracking.
\end{document}"""
    
    response = HttpResponse(latex_source, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="review_status.tex"'
    return response


@login_required
def custom_report(request):
    """Custom report builder"""
    return render(request, 'reports/custom_report.html')


@login_required
def comprehensive_report(request):
    """Generate comprehensive combined report"""
    doc_class = request.GET.get('format', 'report')
    
    generator = LaTeXGenerator(document_class=doc_class)
    latex_source = generator.generate_comprehensive_report()
    
    response = HttpResponse(latex_source, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="comprehensive_report.tex"'
    return response


# FILE: reports/views.py - RISK ASSESSMENT VIEWS
# Add these views to your reports app

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Q, Sum, F
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from decimal import Decimal
import json

from core.models import Output, REFSubmission, SubmissionOutput, Colleague


class OutputRiskDashboardView(LoginRequiredMixin, ListView):
    """
    Main dashboard showing risk profiles across all outputs.
    Provides comprehensive risk analysis and visualizations.
    """
    model = Output
    template_name = 'reports/risk_dashboard.html'
    context_object_name = 'outputs'
    
    def get_queryset(self):
        """Get all outputs, ordered by risk level"""
        return Output.objects.all().select_related('colleague').order_by('-overall_risk_score')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        outputs = Output.objects.all()
        
        # Overall statistics
        context['total_outputs'] = outputs.count()
        context['avg_risk'] = outputs.aggregate(Avg('overall_risk_score'))['overall_risk_score__avg'] or 0
        context['avg_quality'] = sum(o.get_quality_value() for o in outputs) / outputs.count() if outputs.count() > 0 else 0
        
        # Risk distribution
        context['risk_distribution'] = {
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
        
        # Calculate percentages
        total = context['total_outputs']
        if total > 0:
            context['risk_percentages'] = {
                'low': round((context['risk_distribution']['low'] / total) * 100, 1),
                'medium_low': round((context['risk_distribution']['medium_low'] / total) * 100, 1),
                'medium_high': round((context['risk_distribution']['medium_high'] / total) * 100, 1),
                'high': round((context['risk_distribution']['high'] / total) * 100, 1),
            }
        
        # Quality distribution
        context['quality_distribution'] = {
            'four_star': outputs.filter(quality_rating='4*').count(),
            'three_star': outputs.filter(quality_rating='3*').count(),
            'two_star': outputs.filter(quality_rating='2*').count(),
            'one_star': outputs.filter(quality_rating='1*').count(),
            'unclassified': outputs.filter(quality_rating='unclassified').count(),
        }
        
        # Risk by publication status
        context['risk_by_status'] = list(
            outputs.values('status')
            .annotate(
                avg_risk=Avg('overall_risk_score'),
                count=Count('id')
            )
            .order_by('-avg_risk')
        )
        
        # High priority items needing attention
        context['high_risk_outputs'] = outputs.filter(
            overall_risk_score__gte=Decimal('0.75')
        ).order_by('-overall_risk_score')[:10]
        
        # OA compliance issues
        context['oa_compliance_issues'] = outputs.filter(oa_compliance_risk=True).count()
        context['oa_compliance_outputs'] = outputs.filter(oa_compliance_risk=True)[:10]
        
        # REF ready outputs
        context['ref_ready_count'] = sum(1 for o in outputs if o.is_ref_ready())
        context['ref_ready_percentage'] = round(
            (context['ref_ready_count'] / total * 100) if total > 0 else 0, 1
        )
        
        # Quality vs Risk data for scatter plot
        context['quality_risk_data'] = json.dumps([
            {
                'id': o.id,
                'title': o.title[:50],
                'quality': o.get_quality_value(),
                'risk': float(o.overall_risk_score),
                'color': o.get_risk_color(),
                'url': o.get_absolute_url() if hasattr(o, 'get_absolute_url') else '#'
            }
            for o in outputs
        ])
        
        return context


class SubmissionListView(LoginRequiredMixin, ListView):
    """
    List all REF submission scenarios with summary metrics.
    """
    model = REFSubmission
    template_name = 'reports/submission_list.html'
    context_object_name = 'submissions'
    
    def get_queryset(self):
        return REFSubmission.objects.all().prefetch_related('outputs')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate metrics for each submission if not recent
        from django.utils import timezone
        from datetime import timedelta
        
        for submission in context['submissions']:
            # Recalculate if older than 1 hour
            if (not submission.metrics_last_calculated or 
                timezone.now() - submission.metrics_last_calculated > timedelta(hours=1)):
                submission.calculate_all_metrics()
        
        return context


class SubmissionRiskProfileView(LoginRequiredMixin, DetailView):
    """
    Detailed risk profile for a specific REF submission.
    Includes comprehensive analysis and visualizations.
    """
    model = REFSubmission
    template_name = 'reports/submission_risk_profile.html'
    context_object_name = 'submission'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.object
        
        # Recalculate metrics
        submission.calculate_all_metrics()
        
        # Overall portfolio score
        context['portfolio_score'] = submission.get_overall_portfolio_score()
        context['portfolio_score_percentage'] = round(
            (float(context['portfolio_score']) / 4.0) * 100, 1
        )
        
        # Risk distribution
        context['risk_distribution'] = submission.get_risk_distribution()
        total_outputs = submission.outputs.count()
        context['total_outputs'] = total_outputs
        
        if total_outputs > 0:
            context['risk_percentages'] = {
                'low': round((context['risk_distribution']['low'] / total_outputs) * 100, 1),
                'medium_low': round((context['risk_distribution']['medium_low'] / total_outputs) * 100, 1),
                'medium_high': round((context['risk_distribution']['medium_high'] / total_outputs) * 100, 1),
                'high': round((context['risk_distribution']['high'] / total_outputs) * 100, 1),
            }
        
        # Quality distribution
        context['quality_distribution'] = submission.get_quality_distribution()
        
        # High risk outputs
        context['high_risk_outputs'] = submission.get_high_risk_outputs()
        context['medium_high_risk_outputs'] = submission.get_medium_high_risk_outputs()
        
        # OA compliance
        context['oa_issues'] = submission.get_oa_compliance_issues()
        context['has_oa_issues'] = context['oa_issues'].exists()
        
        # Submission readiness
        context['readiness'] = submission.get_submission_readiness()
        
        # Quality vs Risk data for visualization
        outputs = submission.outputs.all()
        context['quality_risk_data'] = json.dumps([
            {
                'id': o.id,
                'title': o.title[:50],
                'quality': o.get_quality_value(),
                'risk': float(o.overall_risk_score),
                'color': o.get_risk_color(),
                'colleague': str(o.colleague) if hasattr(o, 'colleague') else 'Unknown'
            }
            for o in outputs
        ])
        
        # Risk gauge data
        context['avg_risk'] = float(Decimal('1.00') - submission.portfolio_risk_score)
        context['risk_level'] = self._get_risk_level_from_score(context['avg_risk'])
        
        # Metric breakdown
        context['metrics'] = {
            'quality': {
                'score': float(submission.portfolio_quality_score),
                'weight': float(submission.weight_quality),
                'weighted': float(submission.portfolio_quality_score * submission.weight_quality)
            },
            'risk': {
                'score': float(submission.portfolio_risk_score),
                'weight': float(submission.weight_risk),
                'weighted': float(submission.portfolio_risk_score * Decimal('4.00') * submission.weight_risk)
            },
            'representativeness': {
                'score': float(submission.representativeness_score),
                'weight': float(submission.weight_representativeness),
                'weighted': float(submission.representativeness_score * Decimal('4.00') * submission.weight_representativeness)
            },
            'equality': {
                'score': float(submission.equality_score),
                'weight': float(submission.weight_equality),
                'weighted': float(submission.equality_score / Decimal('25.00') * submission.weight_equality)
            },
            'gender_balance': {
                'score': float(submission.gender_balance_score),
                'weight': float(submission.weight_gender_balance),
                'weighted': float(submission.gender_balance_score * Decimal('4.00') * submission.weight_gender_balance)
            }
        }
        
        # Strategic recommendations
        context['recommendations'] = self._generate_recommendations(submission)
        
        return context
    
    def _get_risk_level_from_score(self, risk_score):
        """Convert risk score to level"""
        if risk_score < 0.25:
            return 'low'
        elif risk_score < 0.50:
            return 'medium-low'
        elif risk_score < 0.75:
            return 'medium-high'
        else:
            return 'high'
    
    def _generate_recommendations(self, submission):
        """Generate strategic recommendations based on submission metrics"""
        recommendations = []
        
        # Quality recommendations
        if submission.portfolio_quality_score < Decimal('3.00'):
            recommendations.append({
                'type': 'warning',
                'title': 'Quality Below Target',
                'message': 'Portfolio quality is below 3* average. Consider replacing lower-quality outputs or focusing on upgrading existing outputs.',
                'priority': 'high'
            })
        
        # Risk recommendations
        high_risk_count = submission.get_high_risk_outputs().count()
        total = submission.outputs.count()
        if total > 0 and high_risk_count / total > 0.2:
            recommendations.append({
                'type': 'danger',
                'title': 'High Risk Concentration',
                'message': f'{high_risk_count} outputs ({round(high_risk_count/total*100, 1)}%) are high risk. Consider mitigation strategies or substitutions.',
                'priority': 'critical'
            })
        
        # OA compliance
        if submission.has_oa_compliance_issues():
            oa_count = submission.get_oa_compliance_issues().count()
            recommendations.append({
                'type': 'danger',
                'title': 'Open Access Compliance Issues',
                'message': f'{oa_count} output(s) have OA compliance concerns. These MUST be resolved before submission.',
                'priority': 'critical'
            })
        
        # Equality
        if submission.equality_score < Decimal('80.00'):
            recommendations.append({
                'type': 'info',
                'title': 'Staff Inclusion Opportunity',
                'message': f'Only {submission.equality_score}% of eligible staff are included. Consider broadening submission to increase inclusivity.',
                'priority': 'medium'
            })
        
        # Readiness
        readiness = submission.get_submission_readiness()
        if not readiness['ready']:
            recommendations.append({
                'type': 'warning',
                'title': 'Submission Not Ready',
                'message': f'Readiness: {readiness["readiness_percentage"]:.1f}%. Issues: {", ".join(readiness["issues"])}',
                'priority': 'high'
            })
        
        return recommendations


class SubmissionCreateView(LoginRequiredMixin, CreateView):
    """Create a new REF submission scenario"""
    model = REFSubmission
    template_name = 'reports/submission_form.html'
    fields = [
        'name', 'uoa', 'submission_year', 'description',
        'weight_quality', 'weight_risk', 'weight_representativeness',
        'weight_equality', 'weight_gender_balance'
    ]
    success_url = reverse_lazy('submission-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class SubmissionUpdateView(LoginRequiredMixin, UpdateView):
    """Update a REF submission scenario"""
    model = REFSubmission
    template_name = 'reports/submission_form.html'
    fields = [
        'name', 'uoa', 'submission_year', 'description', 'is_active', 'is_final',
        'weight_quality', 'weight_risk', 'weight_representativeness',
        'weight_equality', 'weight_gender_balance', 'notes'
    ]
    
    def get_success_url(self):
        return reverse_lazy('submission-detail', kwargs={'pk': self.object.pk})


def submission_add_output(request, submission_id, output_id):
    """Add an output to a submission (AJAX endpoint)"""
    if request.method == 'POST':
        submission = get_object_or_404(REFSubmission, pk=submission_id)
        output = get_object_or_404(Output, pk=output_id)
        
        # Get order from request or use next available
        order = request.POST.get('order', submission.outputs.count() + 1)
        
        # Create SubmissionOutput
        so, created = SubmissionOutput.objects.get_or_create(
            submission=submission,
            output=output,
            defaults={'order': order}
        )
        
        if created:
            # Recalculate submission metrics
            submission.calculate_all_metrics()
            return JsonResponse({
                'success': True,
                'message': 'Output added to submission'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Output already in submission'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


def submission_remove_output(request, submission_id, output_id):
    """Remove an output from a submission (AJAX endpoint)"""
    if request.method == 'POST':
        submission = get_object_or_404(REFSubmission, pk=submission_id)
        output = get_object_or_404(Output, pk=output_id)
        
        # Remove SubmissionOutput
        deleted_count, _ = SubmissionOutput.objects.filter(
            submission=submission,
            output=output
        ).delete()
        
        if deleted_count > 0:
            # Recalculate submission metrics
            submission.calculate_all_metrics()
            return JsonResponse({
                'success': True,
                'message': 'Output removed from submission'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Output not found in submission'
            }, status=404)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


def risk_analysis_export(request):
    """Export risk analysis data as JSON"""
    outputs = Output.objects.all()
    
    data = {
        'summary': {
            'total_outputs': outputs.count(),
            'avg_risk': float(outputs.aggregate(Avg('overall_risk_score'))['overall_risk_score__avg'] or 0),
            'risk_distribution': {
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
        },
        'outputs': [
            {
                'id': o.id,
                'title': o.title,
                'risk_score': float(o.overall_risk_score),
                'risk_level': o.get_risk_level(),
                'content_risk': float(o.content_risk_score),
                'timeline_risk': float(o.timeline_risk_score),
                'quality': o.quality_rating,
                'publication_status': o.publication_status,
                'oa_compliance_risk': o.oa_compliance_risk,
            }
            for o in outputs
        ]
    }
    
    return JsonResponse(data)


# URL CONFIGURATION (add to reports/urls.py):
#
# from django.urls import path
# from . import views
#
# urlpatterns = [
#     # Risk Dashboard
#     path('risk-dashboard/', views.OutputRiskDashboardView.as_view(), name='risk-dashboard'),
#     
#     # Submissions
#     path('submissions/', views.SubmissionListView.as_view(), name='submission-list'),
#     path('submissions/create/', views.SubmissionCreateView.as_view(), name='submission-create'),
#     path('submissions/<int:pk>/', views.SubmissionRiskProfileView.as_view(), name='submission-detail'),
#     path('submissions/<int:pk>/edit/', views.SubmissionUpdateView.as_view(), name='submission-update'),
#     
#     # AJAX endpoints
#     path('submissions/<int:submission_id>/add-output/<int:output_id>/', 
#          views.submission_add_output, name='submission-add-output'),
#     path('submissions/<int:submission_id>/remove-output/<int:output_id>/', 
#          views.submission_remove_output, name='submission-remove-output'),
#     
#     # Export
#     path('risk-analysis/export/', views.risk_analysis_export, name='risk-export'),
# ]
#


# ========== Export View Functions ==========

from reports.excel_export import export_risk_analysis_to_excel
from django.shortcuts import get_object_or_404

def export_risk_excel(request):
    """Export risk analysis as Excel"""
    outputs = Output.objects.all()
    return export_risk_analysis_to_excel(outputs)


def export_submission_excel(request, pk):
    """Export submission risk profile as Excel"""
    submission = get_object_or_404(REFSubmission, pk=pk)
    outputs = submission.outputs.all()
    return export_risk_analysis_to_excel(outputs, submission)



# ========== Export View Functions ==========

from reports.excel_export import export_risk_analysis_to_excel
from django.shortcuts import get_object_or_404

def export_risk_excel(request):
    """Export risk analysis as Excel"""
    outputs = Output.objects.all()
    return export_risk_analysis_to_excel(outputs)


def export_submission_excel(request, pk):
    """Export submission risk profile as Excel"""
    submission = get_object_or_404(REFSubmission, pk=pk)
    outputs = submission.outputs.all()
    return export_risk_analysis_to_excel(outputs, submission)

