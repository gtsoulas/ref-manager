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
