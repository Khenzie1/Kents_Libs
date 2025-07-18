# myapp/auth/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password Reset URLs
    path('password-reset-request/', views.forgot_password_request_view, name='password_reset_request'),
    path('password-reset-confirm/', views.forgot_password_confirm_view, name='password_reset_confirm'),
    path('password-reset-resend/', views.resend_password_reset_code_view, name='password_reset_resend'), # NEW URL

    # Existing To-Do List URLs (if they are part of the auth app's responsibility)
    # Assuming these are the primary URLs for the 'myapp' app itself
    path('', views.item_list_create, name='item_list_create'), # This might be your home page after login
    path('create-item/', views.item_list_create, name='item_create'),
    path('update-item/<int:pk>/', views.item_update, name='item_update'),
    path('delete-item/<int:pk>/', views.item_delete, name='item_delete'),
    path('toggle-complete/<int:pk>/', views.item_toggle_complete, name='item_toggle_complete'),

    # Terms and Privacy URLs
    path('terms/', views.terms_of_service_view, name='terms_of_service'),
    path('privacy/', views.privacy_policy_view, name='privacy_policy'),
]
