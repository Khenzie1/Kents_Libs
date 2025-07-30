from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Contact, MessageTemplate, WhatsAppGroup, ScheduledMessage, MessageLog

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'whatsapp_name', 'label', 'track', 'is_active', 'created_at']
    list_filter = ['label', 'track', 'is_active', 'created_at']
    search_fields = ['name', 'whatsapp_name', 'phone_number']
    list_editable = ['label', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'whatsapp_name', 'phone_number')
        }),
        ('Categorization', {
            'fields': ('label', 'track', 'is_active')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )

@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'message_type', 'target_labels', 'is_active', 'created_at']
    list_filter = ['message_type', 'is_active', 'created_at']
    search_fields = ['name', 'content']
    list_editable = ['is_active']

@admin.register(WhatsAppGroup)
class WhatsAppGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'whatsapp_group_name', 'track', 'is_active', 'created_at']
    list_filter = ['track', 'is_active', 'created_at']
    search_fields = ['name', 'whatsapp_group_name']
    list_editable = ['is_active']

@admin.register(ScheduledMessage)
class ScheduledMessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_type', 'get_target', 'scheduled_time', 'status', 'created_at']
    list_filter = ['target_type', 'status', 'scheduled_time', 'created_at']
    search_fields = ['title', 'message_content']
    readonly_fields = ['sent_at']
    
    def get_target(self, obj):
        if obj.target_type == 'individual' and obj.target_contact:
            return obj.target_contact.name
        elif obj.target_type == 'group' and obj.target_group:
            return obj.target_group.name
        elif obj.target_type == 'label_based':
            return f"Label: {obj.target_label}"
        return "No target set"
    get_target.short_description = 'Target'
    
    fieldsets = (
        ('Message Details', {
            'fields': ('title', 'message_content')
        }),
        ('Target Settings', {
            'fields': ('target_type', 'target_contact', 'target_group', 'target_label')
        }),
        ('Scheduling', {
            'fields': ('scheduled_time', 'status')
        }),
        ('Tracking', {
            'fields': ('created_by', 'sent_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_name', 'recipient_type', 'status', 'sent_at', 'get_message_preview']
    list_filter = ['recipient_type', 'status', 'sent_at']
    search_fields = ['recipient_name', 'message_content']
    readonly_fields = ['sent_at']
    
    def get_message_preview(self, obj):
        return obj.message_content[:50] + "..." if len(obj.message_content) > 50 else obj.message_content
    get_message_preview.short_description = 'Message Preview'





# Add to whatsapp_automation/admin.py
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from .tasks import send_welcome_messages_to_new_contacts, cleanup_old_logs

class WhatsAppAutomationAdminSite(admin.AdminSite):
    site_header = "WATRHC WhatsApp Automation Admin"
    site_title = "WATRHC Admin"
    index_title = "Welcome to WATRHC WhatsApp Automation Administration"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-welcome-messages/', self.send_welcome_messages, name='send_welcome_messages'),
            path('cleanup-logs/', self.cleanup_logs, name='cleanup_logs'),
        ]
        return custom_urls + urls
    
    def send_welcome_messages(self, request):
        """Admin action to send welcome messages"""
        task = send_welcome_messages_to_new_contacts.delay()
        messages.success(request, f'Welcome messages task queued. Task ID: {task.id}')
        return redirect('/admin/')
    
    def cleanup_logs(self, request):
        """Admin action to cleanup old logs"""
        task = cleanup_old_logs.delay()
        messages.success(request, f'Log cleanup task queued. Task ID: {task.id}')
        return redirect('/admin/')

# Replace the default admin site
admin_site = WhatsAppAutomationAdminSite(name='admin')

# Register your models with the custom admin site
admin_site.register(Contact, ContactAdmin)
admin_site.register(MessageTemplate, MessageTemplateAdmin)
admin_site.register(WhatsAppGroup, WhatsAppGroupAdmin)
admin_site.register(ScheduledMessage, ScheduledMessageAdmin)
admin_site.register(MessageLog, MessageLogAdmin)