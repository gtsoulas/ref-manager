from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Risk Assessment Framework URLs
    path('risk-dashboard/', views.OutputRiskDashboardView.as_view(), name='risk-dashboard'),
    path('submissions/', views.SubmissionListView.as_view(), name='submission-list'),
    path('submissions/create/', views.SubmissionCreateView.as_view(), name='submission-create'),
    path('submissions/<int:pk>/', views.SubmissionRiskProfileView.as_view(), name='submission-detail'),
    path('submissions/<int:pk>/edit/', views.SubmissionUpdateView.as_view(), name='submission-update'),
    path('submissions/<int:submission_id>/add-output/<int:output_id>/', views.submission_add_output, name='submission-add-output'),
    path('submissions/<int:submission_id>/remove-output/<int:output_id>/', views.submission_remove_output, name='submission-remove-output'),
    path('export/risk-analysis/', views.export_risk_excel, name='risk-export-excel'),
    path('submissions/<int:pk>/export/', views.export_submission_excel, name='submission-export-excel'),
    path('risk-analysis/export-json/', views.risk_analysis_export, name='risk-export'),

    path('', views.reports_home, name='home'),
    path('submission-overview/', views.submission_overview_report, name='submission_overview'),
    path('quality-profile/', views.quality_profile_report, name='quality_profile'),
    path('staff-progress/', views.staff_progress_report, name='staff_progress'),
    path('review-status/', views.review_status_report, name='review_status'),
    path('custom/', views.custom_report, name='custom'),
    path('comprehensive/', views.comprehensive_report, name='comprehensive'),
]