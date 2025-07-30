from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta # Import timedelta
from django.db.models import Count, Q
from .models import Contact, MessageTemplate, ScheduledMessage, MessageLog, WhatsAppGroup
# from .services import WhatsAppAutomationService # Assuming this is correctly imported elsewhere or not strictly needed for these views
from .tasks import send_bulk_dms_async, send_welcome_messages_to_new_contacts # Assuming .tasks exists

import json # Already imported, keeping for clarity


@login_required
def dashboard(request):
    """Main dashboard view"""
    # Get statistics
    total_contacts = Contact.objects.filter(is_active=True).count()
    pending_messages = ScheduledMessage.objects.filter(status='pending').count()
    
    # Calculate Messages Today
    today = timezone.localdate()
    messages_today = MessageLog.objects.filter(sent_at__date=today).count()

    # Calculate Success Rate
    total_sent_messages = MessageLog.objects.count()
    successful_messages = MessageLog.objects.filter(status='success').count()
    success_rate = (successful_messages / total_sent_messages * 100) if total_sent_messages > 0 else 0
    success_rate = round(success_rate, 2) # Round to 2 decimal places

    # Limit recent logs for dashboard summary
    recent_logs = MessageLog.objects.all().order_by('-sent_at')[:5] 
    
    # Contact distribution by label
    label_stats = Contact.objects.filter(is_active=True).values('label').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_contacts': total_contacts,
        'pending_messages': pending_messages,
        'messages_today': messages_today,
        'success_rate': success_rate,
        'recent_logs': recent_logs,
        'label_stats': label_stats,
    }
    
    return render(request, 'whatsapp_automation/dashboard.html', context)


@login_required
def send_bulk_dm(request):
    """Send bulk DMs to contacts with specific label (using Celery)"""
    if request.method == 'POST':
        label = request.POST.get('label')
        message_content = request.POST.get('message_content')
        use_async = request.POST.get('use_async', False) # Check if this is a checkbox/boolean value

        if not label or not message_content:
            messages.error(request, 'Please provide both label and message content')
            return redirect('send_bulk_dm')
        
        # Get contacts with the specified label
        contacts = Contact.objects.filter(label=label, is_active=True)
        
        if not contacts.exists():
            messages.warning(request, f'No active contacts found with label: {label}')
            return redirect('send_bulk_dm')
        
        # Determine if 'use_async' checkbox was checked
        # In HTML forms, unchecked checkboxes don't send their value.
        # So, if use_async is present in POST, it means it was checked.
        if use_async == 'on': # Assuming the checkbox value is 'on' when checked
            # Use Celery for background processing
            contact_ids = list(contacts.values_list('id', flat=True))
            task = send_bulk_dms_async.delay(contact_ids, message_content)
            
            messages.success(
                request, 
                f'Bulk DM task queued for {contacts.count()} contacts with label: {label}. '
                f'Task ID: {task.id}'
            )
        else:
            # Create scheduled message for immediate sending (existing method)
            scheduled_message = ScheduledMessage.objects.create(
                title=f"Bulk DM to {label} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                message_content=message_content,
                target_type='label_based',
                target_label=label,
                scheduled_time=timezone.now(),
                created_by=request.user,
                status='pending'
            )
            
            messages.success(request, f'Bulk DM scheduled for {contacts.count()} contacts with label: {label}')
        
        return redirect('dashboard')
    
    # GET request - show form (same as before)
    labels = Contact.objects.filter(is_active=True).values_list('label', flat=True).distinct()
    templates = MessageTemplate.objects.filter(is_active=True)
    
    context = {
        'labels': labels,
        'templates': templates,
    }
    
    return render(request, 'whatsapp_automation/send_bulk_dm.html', context)

@login_required
def schedule_message(request):
    """Schedule a message for future sending"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message_content = request.POST.get('message_content')
        target_type = request.POST.get('target_type')
        scheduled_time = request.POST.get('scheduled_time')
        
        # Validate required fields
        if not all([title, message_content, target_type, scheduled_time]):
            messages.error(request, 'Please fill in all required fields')
            return redirect('schedule_message')
        
        try:
            # Ensure scheduled_time is parsed correctly as a datetime object
            # fromisoformat handles 'T' directly. For older Python versions, replace 'T' with space.
            # Assuming scheduled_time comes in 'YYYY-MM-DDTHH:MM' format from datetime-local input
            scheduled_time = timezone.datetime.fromisoformat(scheduled_time)
            if timezone.is_naive(scheduled_time):
                scheduled_time = timezone.make_aware(scheduled_time)
        except ValueError:
            messages.error(request, 'Invalid datetime format. Please use YYYY-MM-DDTHH:MM.')
            return redirect('schedule_message')
        
        # Create scheduled message object
        scheduled_message = ScheduledMessage(
            title=title,
            message_content=message_content,
            target_type=target_type,
            scheduled_time=scheduled_time,
            created_by=request.user
        )
        
        # Set target based on type
        if target_type == 'individual':
            contact_id = request.POST.get('target_contact')
            if contact_id:
                scheduled_message.target_contact_id = contact_id
            else:
                messages.error(request, 'Please select a target contact for individual messages.')
                return redirect('schedule_message')
        elif target_type == 'group':
            group_id = request.POST.get('target_group')
            if group_id:
                scheduled_message.target_group_id = group_id
            else:
                messages.error(request, 'Please select a target group for group messages.')
                return redirect('schedule_message')
        elif target_type == 'label_based':
            target_label = request.POST.get('target_label')
            if target_label:
                scheduled_message.target_label = target_label
            else:
                messages.error(request, 'Please select a target label for label-based messages.')
                return redirect('schedule_message')
        
        scheduled_message.save()
        messages.success(request, f'Message "{title}" scheduled successfully')
        return redirect('dashboard')
    
    # GET request - show form
    contacts = Contact.objects.filter(is_active=True)
    groups = WhatsAppGroup.objects.filter(is_active=True)
    labels = Contact.objects.filter(is_active=True).values_list('label', flat=True).distinct()
    templates = MessageTemplate.objects.filter(is_active=True)
    
    context = {
        'contacts': contacts,
        'groups': groups,
        'labels': labels,
        'templates': templates,
    }
    
    return render(request, 'whatsapp_automation/schedule_message.html', context)

@login_required
def message_logs(request):
    """View message logs (initial HTML render)"""
    logs = MessageLog.objects.all().order_by('-sent_at')
    
    # Filter by status if provided (for initial page load)
    status_filter = request.GET.get('status')
    if status_filter:
        logs = logs.filter(status=status_filter)
    
    context = {
        'logs': logs,
        'status_filter': status_filter,
    }
    
    return render(request, 'whatsapp_automation/message_logs.html', context)

@login_required
def get_template_content(request):
    """AJAX endpoint to get template content"""
    template_id = request.GET.get('template_id')
    if template_id:
        try:
            template = MessageTemplate.objects.get(id=template_id)
            return JsonResponse({'content': template.content})
        except MessageTemplate.DoesNotExist:
            pass
    
    return JsonResponse({'content': ''})

# --- NEW API ENDPOINTS FOR DYNAMIC UPDATES ---

@login_required
def get_dashboard_stats(request):
    """AJAX endpoint to get dashboard statistics."""
    total_contacts = Contact.objects.filter(is_active=True).count()
    pending_messages = ScheduledMessage.objects.filter(status='pending').count()
    
    today = timezone.localdate()
    messages_today = MessageLog.objects.filter(sent_at__date=today).count()

    total_sent_messages = MessageLog.objects.count()
    successful_messages = MessageLog.objects.filter(status='success').count()
    success_rate = (successful_messages / total_sent_messages * 100) if total_sent_messages > 0 else 0
    success_rate = round(success_rate, 2)

    data = {
        'total_contacts': total_contacts,
        'pending_messages': pending_messages,
        'messages_today': messages_today,
        'success_rate': success_rate,
    }
    return JsonResponse(data)

@login_required
def get_contact_distribution(request):
    """AJAX endpoint to get contact distribution by label."""
    label_stats = list(Contact.objects.filter(is_active=True).values('label').annotate(
        count=Count('id')
    ).order_by('-count'))
    # JsonResponse requires dictionary keys to be strings
    return JsonResponse({'label_stats': label_stats})

from django.db.models import Max, OuterRef, Subquery, Q

@login_required
def get_recent_message_activity(request):
    """
    AJAX endpoint to get recent message activity, showing the latest status
    for each unique message to a recipient using a subquery approach (database-agnostic).
    """
    # 1. Create a subquery to find the latest sent_at for each unique
    #    (recipient_name, message_content) combination.
    #    We annotate to find the max_sent_at and order_by() to clear default ordering
    #    which can interfere with distinct/grouping.
    latest_per_message_recipient = MessageLog.objects.values(
        'recipient_name', 'message_content'
    ).annotate(
        max_sent_at=Max('sent_at')
    ).order_by() # Important: clear any default ordering here for the subquery
    
    # Fetch the results of the subquery first
    latest_timestamps = list(latest_per_message_recipient.values(
        'recipient_name', 'message_content', 'max_sent_at'
    ))

    # Build a complex Q object to filter the main queryset
    q_objects = Q()
    for item in latest_timestamps:
        q_objects |= Q(
            recipient_name=item['recipient_name'],
            message_content=item['message_content'],
            sent_at=item['max_sent_at']
        )
    
    # Apply the filter to the main logs queryset
    # If no items in latest_timestamps, logs will be empty, which is correct.
    if latest_timestamps:
        recent_logs = MessageLog.objects.filter(q_objects).order_by('-sent_at')[:5]
    else:
        recent_logs = MessageLog.objects.none() # Return an empty queryset if no logs

    logs_data = []
    for log in recent_logs:
        logs_data.append({
            'recipient_name': log.recipient_name,
            'sent_at': timezone.localtime(log.sent_at).strftime("%b %d, %H:%M"), 
            'status': log.status,
        })
    return JsonResponse({'recent_logs': logs_data})

@login_required
def get_message_log_details(request, log_id):
    """AJAX endpoint to get full details of a specific message log."""
    log = get_object_or_404(MessageLog, pk=log_id)
    data = {
        'recipient_name': log.recipient_name,
        'recipient_type': log.recipient_type,
        'message_content': log.message_content,
        'status': log.status,
        'sent_at': timezone.localtime(log.sent_at).isoformat(), # Use ISO format for JS parsing
        'error_message': getattr(log, 'error_message', None), # Safely get error_message, or None if it doesn't exist
    }
    return JsonResponse(data)

from django.db.models import Max

@login_required
def get_filtered_message_logs_api(request):
    """AJAX endpoint to get filtered message logs, showing the latest status for each unique message to a recipient."""
    
    # 1. Get the latest sent_at timestamp for each unique (recipient_name, message_content)
    # This identifies the "most recent" log for a given logical message
    latest_logs_subquery = MessageLog.objects.values('recipient_name', 'message_content').annotate(
        max_sent_at=Max('sent_at')
    ).order_by() # Remove default ordering for subquery for potential performance
    
    logs = MessageLog.objects.filter(
        (Q(recipient_name__in=[item['recipient_name'] for item in latest_logs_subquery]) &
         Q(message_content__in=[item['message_content'] for item in latest_logs_subquery]) &
         Q(sent_at__in=[item['max_sent_at'] for item in latest_logs_subquery]))
    ).order_by('-sent_at') # Order the final results

    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        logs = logs.filter(status=status_filter)
    
    # Max 50 messages for this AJAX response to keep it performant
    logs = logs[:50]

    # Serialize logs to a list of dictionaries, including formatted data for frontend
    logs_data = []
    for log in logs:
        logs_data.append({
            'id': log.id,
            'recipient_name': log.recipient_name,
            'recipient_type': log.recipient_type,
            'message_content_preview': (log.message_content[:80] + '...') if len(log.message_content) > 80 else log.message_content,
            'status': log.status,
            'sent_at_date': timezone.localtime(log.sent_at).strftime("%b %d, %Y"),
            'sent_at_time': timezone.localtime(log.sent_at).strftime("%H:%M"),
            'icon_class_type': 'user' if log.recipient_type == 'contact' else 'users',
            'icon_class_status': 'check' if log.status == 'success' else ('times' if log.status == 'failed' else 'clock'),
            'badge_color_status': 'success' if log.status == 'success' else ('danger' if log.status == 'failed' else 'warning'),
        })
    
    return JsonResponse({'logs': logs_data, 'count': len(logs_data)})