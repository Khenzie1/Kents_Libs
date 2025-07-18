# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include your app's main URLs
    path('', include('myapp.urls')),
    # Include the new authentication URLs
    path('auth/', include('myapp.auth.urls')),
]
