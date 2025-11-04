from django.urls import path
from . import views
from . import views_export

urlpatterns = [
#    path('import/', views.import_data, name='import_data'),
#    path('import/colleagues/', views.import_colleagues_excel, name='import_colleagues_excel'),
#    path('import/outputs/', views.import_outputs_excel, name='import_outputs_excel'),
#    path('import/critical-friends/', views.import_critical_friends_excel, name='import_critical_friends_excel'),
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Colleagues
    path('colleagues/', views.colleague_list, name='colleague_list'),
    path('colleagues/<int:pk>/', views.colleague_detail, name='colleague_detail'),
    path('colleagues/create/', views.colleague_create, name='colleague_create'),
    path('colleagues/<int:pk>/update/', views.colleague_update, name='colleague_update'),
    path('colleagues/<int:pk>/mark-former/', views.colleague_mark_as_former, name='colleague_mark_former'),
    path('colleagues/duplicates/', views.find_duplicate_colleagues, name='find_duplicate_colleagues'),
    path('colleagues/merge/', views.merge_colleagues, name='merge_colleagues'),
    path('colleagues/<int:colleague_id>/update-category/', views.update_colleague_category, name='update_colleague_category'),


    # Outputs
    path('outputs/', views.output_list, name='output_list'),
    path('outputs/<int:pk>/', views.output_detail, name='output_detail'),
    path('outputs/create/', views.output_create, name='output_create'),
    path('outputs/<int:pk>/update/', views.output_update, name='output_update'),
    path('outputs/<int:pk>/delete/', views.output_delete, name='output_delete'),
 #   path('outputs/<int:pk>/approve/', views.output_approve, name='output_approve'),
    
    # Critical Friends
    path('critical-friends/', views.critical_friend_list, name='critical_friend_list'),
    path('critical-friends/<int:pk>/', views.critical_friend_detail, name='critical_friend_detail'),
    path('critical-friends/create/', views.critical_friend_create, name='critical_friend_create'),
    path('critical-friends/<int:pk>/update/', views.critical_friend_update, name='critical_friend_update'),
    path('outputs/<int:output_id>/assign-critical-friend/', views.assign_critical_friend, name='assign_critical_friend'),

   # Task URLs
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/dashboard/', views.task_dashboard, name='task_dashboard'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),

    # Requests
    path('requests/', views.request_list, name='request_list'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/create/', views.request_create, name='request_create'),
    path('requests/<int:pk>/update/', views.request_update, name='request_update'),
    path('requests/<int:pk>/complete/', views.request_complete, name='request_complete'),
    path('requests/<int:pk>/delete/', views.request_delete, name='request_delete'),

    
    # Internal Panel URLs
    path('internal-panel/', views.internal_panel_list, name='internal_panel_list'),
    path('internal-panel/<int:pk>/', views.internal_panel_detail, name='internal_panel_detail'),
    path('internal-panel/create/', views.internal_panel_create, name='internal_panel_create'),
    path('internal-panel/<int:pk>/update/', views.internal_panel_update, name='internal_panel_update'),
    path('outputs/<int:output_pk>/assign-internal-panel/', views.assign_internal_panel, name='assign_internal_panel'),
    path('internal-panel-assignment/<int:pk>/update/', views.internal_panel_assignment_update, name='internal_panel_assignment_update'),
    path('internal-panel-assignment/<int:pk>/delete/', 
         views.internal_panel_assignment_delete, 
         name='internal_panel_assignment_delete'),
    path('critical-friend-assignment/<int:pk>/delete/', 
         views.critical_friend_assignment_delete, 
         name='critical_friend_assignment_delete'),

path('outputs/import/', views.import_outputs, name='import_outputs'),

    # Export routes
    path('export/assignments/', views_export.export_assignments_view, name='export_assignments'),
    path('export/assignments/excel/', views_export.export_assignments_excel, name='export_assignments_excel'),
    path('export/assignments/csv/', views_export.export_assignments_csv, name='export_assignments_csv'),


]
