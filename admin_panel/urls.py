from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/suspend/', views.user_suspend, name='user_suspend'),
    path('users/<int:user_id>/activate/', views.user_activate, name='user_activate'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    
    # Booking Management
    path('bookings/', views.booking_management, name='booking_management'),
    
    # System Settings
    path('settings/', views.system_settings, name='system_settings'),
    
    # Activity Logs
    path('activity-log/', views.admin_activity_log, name='activity_log'),
    path('user-activity-log/', views.user_activity_log, name='user_activity_log'),
    
    # AJAX endpoints
    path('ajax/user-stats/', views.ajax_user_stats, name='ajax_user_stats'),
    path('ajax/users/<int:user_id>/suspend/', views.ajax_suspend_user, name='ajax_suspend_user'),
    path('ajax/users/<int:user_id>/activate/', views.ajax_activate_user, name='ajax_activate_user'),
]
