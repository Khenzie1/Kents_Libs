# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list_create, name='item_list_create'),
    path('create-item/', views.item_list_create, name='item_create'), # Assuming this was your create path
    path('update-item/<int:pk>/', views.item_update, name='item_update'),
    path('delete-item/<int:pk>/', views.item_delete, name='item_delete'),
    path('toggle-complete/<int:pk>/', views.item_toggle_complete, name='item_toggle_complete'),
    # Removed: terms_of_service and privacy_policy views as they were part of auth flow
]
