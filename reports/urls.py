from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='home'),
    path('submission-overview/', views.submission_overview_report, name='submission_overview'),
    path('quality-profile/', views.quality_profile_report, name='quality_profile'),
    path('staff-progress/', views.staff_progress_report, name='staff_progress'),
    path('review-status/', views.review_status_report, name='review_status'),
    path('custom/', views.custom_report, name='custom'),
    path('comprehensive/', views.comprehensive_report, name='comprehensive'),
]