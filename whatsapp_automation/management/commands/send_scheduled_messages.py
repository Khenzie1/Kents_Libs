from django.core.management.base import BaseCommand
from django.utils import timezone
from whatsapp_automation.models import ScheduledMessage, Contact
from whatsapp_automation.services import WhatsAppAutomationService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process and send scheduled WhatsApp messages'
    
    def handle(self, *args, **options):
        # Get pending messages that are due
        now = timezone.now()
        pending_messages = ScheduledMessage.objects.filter(
            status='pending',
            scheduled_time__lte=now
        ).order_by('scheduled_time')
        
        if not pending_messages.exists():
            self.stdout.write("No pending messages to send")
            return
        
        # Initialize WhatsApp service
        whatsapp_service = WhatsAppAutomationService()
        
        try:
            # Login to WhatsApp
            if not whatsapp_service.login_to_whatsapp():
                self.stdout.write(self.style.ERROR("Failed to login to WhatsApp"))
                return
            
            # Process each scheduled message
            for message in pending_messages:
                self.stdout.write(f"Processing: {message.title}")
                
                try:
                    if message.target_type == 'individual' and message.target_contact:
                        # Send to individual contact
                        success = whatsapp_service.send_dm_to_contact(
                            message.target_contact,
                            message.message_content
                        )
                        
                    elif message.target_type == 'group' and message.target_group:
                        # Send to group
                        success = whatsapp_service.send_group_message(
                            message.target_group,
                            message.message_content
                        )
                        
                    elif message.target_type == 'label_based' and message.target_label:
                        # Send to all contacts with specific label
                        contacts = Contact.objects.filter(
                            label=message.target_label,
                            is_active=True
                        )
                        
                        if contacts.exists():
                            results = whatsapp_service.send_bulk_dms(
                                contacts,
                                message.message_content,
                                delay=60  # 1 minute delay between messages
                            )
                            success = any(result['success'] for result in results)
                        else:
                            success = False
                            
                    else:
                        success = False
                        self.stdout.write(
                            self.style.WARNING(f"Invalid target configuration for: {message.title}")
                        )
                    
                    # Update message status
                    if success:
                        message.status = 'sent'
                        message.sent_at = timezone.now()
                        self.stdout.write(
                            self.style.SUCCESS(f"Successfully sent: {message.title}")
                        )
                    else:
                        message.status = 'failed'
                        self.stdout.write(
                            self.style.ERROR(f"Failed to send: {message.title}")
                        )
                    
                    message.save()
                    
                except Exception as e:
                    message.status = 'failed'
                    message.save()
                    self.stdout.write(
                        self.style.ERROR(f"Error processing {message.title}: {str(e)}")
                    )
        
        finally:
            # Don't close the browser automatically to keep WhatsApp session active
            # whatsapp_service.close()
            pass