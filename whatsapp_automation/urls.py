# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('send-bulk-dm/', views.send_bulk_dm, name='send_bulk_dm'),
#     path('schedule-message/', views.schedule_message, name='schedule_message'),
#     path('message-logs/', views.message_logs, name='message_logs'),
#     path('api/template-content/', views.get_template_content, name='get_template_content'),
# ]




from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('send-bulk-dm/', views.send_bulk_dm, name='send_bulk_dm'),
    path('schedule-message/', views.schedule_message, name='schedule_message'),
    path('message-logs/', views.message_logs, name='message_logs'),
    path('api/template-content/', views.get_template_content, name='get_template_content'),

    # New API endpoints for Dashboard and Message Logs
    path('api/dashboard-stats/', views.get_dashboard_stats, name='api_dashboard_stats'),
    path('api/contact-distribution/', views.get_contact_distribution, name='api_contact_distribution'),
    path('api/recent-message-activity/', views.get_recent_message_activity, name='api_recent_message_activity'),
    path('api/message-logs/<int:log_id>/', views.get_message_log_details, name='api_message_log_details'),
    path('api/message-logs-filtered/', views.get_filtered_message_logs_api, name='api_filtered_message_logs'), 
]