from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Contact(models.Model):
    LABEL_CHOICES = [
        ('WATRHC', 'WATRHC'),
        ('UI/UX', 'UI/UX'),
        ('Python Programmer', 'Python Programmer'),
        ('Data Analytics', 'Data Analytics'),
        ('Web Development', 'Web Development'),
        ('Intern', 'Intern'),
        ('Paid', 'Paid'),
        ('Follow-up', 'Follow-up'),
        ('No Response', 'No Response'),
        ('Check-In', 'Check-In'),
        ('Ready for DM', 'Ready for DM'),
    ]
    
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    whatsapp_name = models.CharField(max_length=100, help_text="Name as it appears in WhatsApp")
    label = models.CharField(max_length=50, choices=LABEL_CHOICES)
    track = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.label})"
    
    class Meta:
        ordering = ['name']

class MessageTemplate(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('welcome', 'Welcome Message'),
        ('follow_up', 'Follow-up Message'),
        ('check_in', 'Check-in Message'),
        ('tip', 'Tip/Insight'),
        ('motivation', 'Motivational Message'),
        ('quiz', 'Quiz Link'),
        ('custom', 'Custom Message'),
    ]
    
    name = models.CharField(max_length=100)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField(help_text="Use {name} for personalization")
    target_labels = models.CharField(max_length=200, help_text="Comma-separated labels")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class WhatsAppGroup(models.Model):
    name = models.CharField(max_length=100)
    whatsapp_group_name = models.CharField(max_length=100, help_text="Group name as it appears in WhatsApp")
    track = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ScheduledMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    MESSAGE_TARGET_CHOICES = [
        ('individual', 'Individual Contact'),
        ('group', 'WhatsApp Group'),
        ('label_based', 'Label-based (Multiple Contacts)'),
    ]
    
    title = models.CharField(max_length=100)
    message_content = models.TextField()
    target_type = models.CharField(max_length=20, choices=MESSAGE_TARGET_CHOICES)
    target_contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE)
    target_group = models.ForeignKey(WhatsAppGroup, null=True, blank=True, on_delete=models.CASCADE)
    target_label = models.CharField(max_length=50, blank=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_time}"
    
    class Meta:
        ordering = ['scheduled_time']

class MessageLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        # ('pending', 'Pending'),
        ('skipped', 'Skipped'),
    ]
    
    recipient_name = models.CharField(max_length=100)
    recipient_type = models.CharField(max_length=20)  # contact, group
    message_content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    scheduled_message = models.ForeignKey(ScheduledMessage, null=True, blank=True, on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.recipient_name} - {self.status} - {self.sent_at}"
    
    class Meta:
        ordering = ['-sent_at']