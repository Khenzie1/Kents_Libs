# myapp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _ # Import for translatable strings
from .models import CustomUser, Item

# Register your CustomUser model
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Display fields in the list view
    list_display = ('email', 'username', 'is_staff', 'is_active')
    
    # Fields to use when adding a user (for the 'Add User' form)
    # This is typically fine as it explicitly lists all fields for creation.
    add_fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'password2')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    # Fields to use when changing an existing user (for the 'Change User' form)
    # We explicitly define the fieldsets to avoid duplication issues with UserAdmin's defaults.
    fieldsets = (
        (None, {'fields': ('email', 'password')}), # Email is our USERNAME_FIELD
        (_('Personal info'), {'fields': ('username',)}), # Our 'Full Name' field
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Fields to search by
    search_fields = ('email', 'username')
    # Fields to filter by
    ordering = ('email',)

admin.site.register(Item)
