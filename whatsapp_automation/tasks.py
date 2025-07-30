import time
import logging
import psutil # For optional process cleanup
from django.utils import timezone
from django.db.models import Q
from celery import shared_task
from celery.signals import worker_shutdown
from datetime import timedelta
from celery.exceptions import Retry

# Import the necessary exceptions from selenium
from selenium.common.exceptions import TimeoutException, WebDriverException

# Import the singleton getter function for WhatsAppAutomationService
from .services import get_whatsapp_automation_service, _whatsapp_automation_service_instance, _service_lock
from .models import ScheduledMessage, Contact, MessageLog, WhatsAppGroup # Ensure these models are correctly imported

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=300)  # Increased max_retries for robustness
def process_scheduled_messages(self):
    """
    Background task to process scheduled messages with improved error handling and service management.
    """
    try:
        logger.info(f"Task {self.request.id}: Checking for pending messages...")

        # Get pending messages that are due
        now = timezone.now()
        pending_messages = ScheduledMessage.objects.filter(
            status='pending',
            scheduled_time__lte=now
        ).order_by('scheduled_time')

        if not pending_messages.exists():
            logger.info(f"Task {self.request.id}: No pending messages to process.")
            return "No pending messages to process"

        # Get the singleton WhatsApp service instance with retry logic
        whatsapp_service = None
        try:
            whatsapp_service = get_whatsapp_automation_service()
            if not whatsapp_service: # get_whatsapp_automation_service will raise if it fails critically
                raise Exception("Failed to obtain WhatsApp service after initialization attempts.")
            logger.info("WhatsApp service obtained successfully for task processing.")
        except Exception as e:
            logger.error(f"Task {self.request.id}: Critical error getting WhatsApp service: {e}")
            # If we can't even get the service, retry the whole task
            raise self.retry(exc=e, countdown=60) # Retry after 60 seconds

        total_processed = 0
        total_failed = 0

        for message in pending_messages:
            recipient_name = ""
            recipient_type = ""
            message_sent_successfully = False
            log_error_message = ""

            # Use a nested try-except for individual message processing
            try:
                if message.target_contact:
                    recipient_name = message.target_contact.whatsapp_name
                    recipient_type = "contact"
                    logger.info(f"Processing message for contact: {recipient_name}")
                    message_sent_successfully = whatsapp_service.send_message(
                        recipient_type="contact",
                        recipient_name=recipient_name,
                        message_content=message.message_content
                    )
                elif message.target_group:
                    recipient_name = message.target_group.name
                    recipient_type = "group"
                    logger.info(f"Processing message for group: {recipient_name}")
                    message_sent_successfully = whatsapp_service.send_message(
                        recipient_type="group",
                        recipient_name=recipient_name,
                        message_content=message.message_content
                    )
                elif message.target_label:
                    logger.info(f"Processing label-based message for label: {message.target_label}")
                    contacts_to_message = Contact.objects.filter(label=message.target_label, is_active=True)
                    # Corrected line here:
                    if not contacts_to_message.exists():
                        logger.info(f"No active contacts found for label: {message.target_label}. Skipping this message.")
                        MessageLog.objects.create(
                            recipient_name=f"Label: {message.target_label}",
                            recipient_type="label",
                            message_content=message.message_content,
                            status='skipped',
                            error_message="No active contacts found for this label.",
                            scheduled_message=message
                        )
                        message.status = 'skipped'
                        message.sent_at = timezone.now()
                        message.save()
                        total_processed += 1 # Count as processed but skipped
                        continue

                    label_sent_count = 0
                    label_fail_count = 0
                    for contact in contacts_to_message:
                        recipient_name = contact.whatsapp_name
                        recipient_type = "contact"
                        logger.info(f"Attempting to send message to label contact: {recipient_name}")
                        individual_message_sent = whatsapp_service.send_message(
                            recipient_type="contact",
                            recipient_name=recipient_name,
                            message_content=message.message_content
                        )
                        if individual_message_sent:
                            label_sent_count += 1
                            #Check if message log already exists before creating a new one
                            if not MessageLog.objects.filter(recipient_name=recipient_name, scheduled_message=message, status='success').exists():
                                MessageLog.objects.create(
                                    recipient_name=recipient_name,
                                    recipient_type="contact",
                                    message_content=message.message_content,
                                    status='success',
                                    scheduled_message=message
                            )
                        else:
                            label_fail_count += 1
                            log_error_message = f"Failed to send to {recipient_name} for label '{message.target_label}'."
                            if not MessageLog.objects.filter(recipient_name=recipient_name, scheduled_message=message, status='failed').exists():
                                MessageLog.objects.create(
                                    recipient_name=recipient_name,
                                    recipient_type="contact",
                                    message_content=message.message_content,
                                    status='failed',
                                    error_message=log_error_message,
                                    scheduled_message=message
                            ) #Integrated Logic to prevent duplicate log entries

                    if label_sent_count > 0:
                        message_sent_successfully = True # At least one message was sent for the label
                    logger.info(f"Label-based messaging: {label_sent_count}/{len(contacts_to_message)} messages sent successfully")
                    if label_fail_count > 0:
                        total_failed += label_fail_count # Update total failed count
                        if not message_sent_successfully: # Only set overall message status to failed if no messages were sent
                            log_error_message = f"{label_fail_count} messages failed for label '{message.target_label}'"
                else:
                    logger.warning(f"Scheduled message {message.id} has no valid recipient (contact, group, or label). Skipping.")
                    MessageLog.objects.create(
                        recipient_name="N/A",
                        recipient_type="N/A",
                        message_content=message.message_content,
                        status='skipped',
                        error_message="No valid recipient specified.",
                        scheduled_message=message
                    )
                    message.status = 'skipped'
                    message.sent_at = timezone.now()
                    message.save()
                    total_processed += 1
                    continue

                # Update ScheduledMessage status and create MessageLog for single recipient/overall label status
                if message_sent_successfully:
                    message.status = 'sent'
                    total_processed += 1
                    # A MessageLog for single recipient is created within the loop for label-based.
                    # For contact/group, it's created here.
                    if message.target_contact or message.target_group:
                        MessageLog.objects.create(
                            recipient_name=recipient_name,
                            recipient_type=recipient_type,
                            message_content=message.message_content,
                            status='success',
                            scheduled_message=message
                        )
                else:
                    message.status = 'failed'
                    total_failed += 1
                    # A MessageLog for single recipient is created within the loop for label-based.
                    # For contact/group, it's created here.
                    if message.target_contact or message.target_group or (message.target_label and log_error_message):
                        MessageLog.objects.create(
                            recipient_name=recipient_name,
                            recipient_type=recipient_type,
                            message_content=message.message_content,
                            status='failed',
                            error_message=log_error_message if log_error_message else "Message sending failed or could not be confirmed.",
                            scheduled_message=message
                        )

                message.sent_at = timezone.now()
                message.save()

            except (TimeoutException, WebDriverException) as e:
                log_error_message = f"WebDriver/Timeout error for {recipient_name} while processing {message.title}: {e}"
                logger.error(log_error_message)
                message.status = 'failed'
                message.sent_at = timezone.now()
                message.save()
                total_failed += 1
                MessageLog.objects.create(
                    recipient_name=recipient_name,
                    recipient_type=recipient_type,
                    message_content=message.message_content,
                    status='failed',
                    error_message=log_error_message,
                    scheduled_message=message
                )
                # If a WebDriver issue occurs for one message, it might affect others.
                # Retry the whole task if it's the first attempt, or a severe error.
                if self.request.retries < self.max_retries:
                    logger.info(f"Retrying task {self.request.id} due to WebDriver error. Attempt {self.request.retries + 1}/{self.max_retries}.")
                    raise self.retry(exc=e, countdown=60) # Retry after 60 seconds
                else:
                    logger.critical(f"Max retries reached for task {self.request.id} after WebDriver error. Failing task.")
                    # Let the task fail normally after max retries
                    pass


            except Exception as e:
                log_error_message = f"An unexpected error occurred for {recipient_name} while processing {message.title}: {e}"
                logger.error(log_error_message)
                message.status = 'failed'
                message.sent_at = timezone.now()
                message.save()
                total_failed += 1
                MessageLog.objects.create(
                    recipient_name=recipient_name,
                    recipient_type=recipient_type,
                    message_content=message.message_content,
                    status='failed',
                    error_message=log_error_message,
                    scheduled_message=message
                )
                # For unexpected errors, still retry the task if within limits
                if self.request.retries < self.max_retries:
                    logger.info(f"Retrying task {self.request.id} due to unexpected error. Attempt {self.request.retries + 1}/{self.max_retries}.")
                    raise self.retry(exc=e, countdown=30) # Retry after 30 seconds
                else:
                    logger.critical(f"Max retries reached for task {self.request.id} after unexpected error. Failing task.")
                    pass


        logger.info(f"Task {self.request.id}: Processed {total_processed} messages successfully, {total_failed} failed.")
        return f"Processed {total_processed} messages successfully, {total_failed} failed."

    except Exception as e:
        logger.critical(f"Critical unhandled error in process_scheduled_messages task {self.request.id}: {e}", exc_info=True)
        # If a critical error occurs even before processing messages, retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task {self.request.id} due to critical error. Attempt {self.request.retries + 1}/{self.max_retries}.")
            raise self.retry(exc=e, countdown=60)
        else:
            logger.critical(f"Max retries reached for task {self.request.id} after critical error. Failing task.")
            raise # Re-raise to let Celery mark the task as failed

@shared_task(bind=True)
def cleanup_old_logs(self):
    """
    Cleans up MessageLog entries older than a specified duration.
    """
    logger.info("Starting cleanup of old message logs...")
    try:
        threshold = timezone.now() - timedelta(days=90) # Example: delete logs older than 90 days
        old_logs_count = MessageLog.objects.filter(sent_at__lte=threshold).count()
        MessageLog.objects.filter(sent_at__lte=threshold).delete()
        logger.info(f"Cleaned up {old_logs_count} old message logs.")
        return f"Cleaned up {old_logs_count} old message logs."
    except Exception as e:
        logger.error(f"Error during log cleanup: {e}")
        raise

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_bulk_dms_async(self, message_id):
    """ Task to asynchronously send bulk DMs. """
    logger.info(f"Received request to send bulk DM with ID: {message_id}")
    try:
        scheduled_message = ScheduledMessage.objects.get(id=message_id)
        whatsapp_service = get_whatsapp_automation_service()
        if scheduled_message.target_type == 'label_based':
            contacts = Contact.objects.filter(label=scheduled_message.target_label)
            for contact in contacts:
                whatsapp_service.send_message("contact", contact.whatsapp_name, scheduled_message.message_content)
        elif scheduled_message.target_type == 'individual':
            whatsapp_service.send_message("contact", scheduled_message.target_contact.whatsapp_name, scheduled_message.message_content)
        elif scheduled_message.target_type == 'group':
            whatsapp_service.send_message("group", scheduled_message.target_group.whatsapp_group_name, scheduled_message.message_content)
        logger.info(f"Bulk DM {message_id} processed successfully.")
        return f"Bulk DM {message_id} processed successfully."
    except Exception as e:
        logger.error(f"Failed to send bulk DM {message_id}: {e}")
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_messages_to_new_contacts(self, contact_id):
    """
    Task to send welcome messages to new contacts.
    """
    logger.info(f"Received request to send welcome message to new contact ID: {contact_id}")
    try:
        contact = Contact.objects.get(id=contact_id)
        whatsapp_service = get_whatsapp_automation_service()
        if whatsapp_service:
            message_content = f"Hello {contact.whatsapp_name}, welcome!" # Customize your welcome message
            if whatsapp_service.send_message(recipient_type="contact", recipient_name=contact.whatsapp_name, message_content=message_content):
                logger.info(f"Welcome message sent to {contact.whatsapp_name}.")
                return f"Welcome message sent to {contact.whatsapp_name}."
            else:
                raise Exception(f"Failed to send welcome message to {contact.whatsapp_name}.")
        else:
            raise Exception("Failed to obtain WhatsApp service for welcome message.")
    except Contact.DoesNotExist:
        logger.error(f"Contact with ID {contact_id} not found for welcome message.")
        return f"Contact with ID {contact_id} not found."
    except Exception as e:
        logger.error(f"Error sending welcome message to contact {contact_id}: {e}")
        raise self.retry(exc=e)

@worker_shutdown.connect
def shutdown_webdriver(sender, **kwargs):
    """
    Signal handler to ensure WebDriver is gracefully closed when the Celery worker shuts down.
    """
    logger.info("Celery worker shutdown signal received. Attempting to close WebDriver.")
    with _service_lock:
        global _whatsapp_automation_service_instance
        if _whatsapp_automation_service_instance is not None:
            try:
                _whatsapp_automation_service_instance.close()
                logger.info("WebDriver closed successfully during worker shutdown.")
            except Exception as e:
                logger.error(f"Error closing WebDriver during shutdown: {e}")
            finally:
                _whatsapp_automation_service_instance = None # Ensure instance is reset
        else:
            logger.info("No WebDriver instance found during worker shutdown.")

    # Optional: Force cleanup any remaining Chrome processes. Use with caution.
    # This is a fallback and generally should not be needed if .close() works.
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            # Check for both 'chrome' and 'chromedriver' process names
            if 'chrome' in proc.info['name'].lower() or 'chromedriver' in proc.info['name'].lower():
                try:
                    # Attempt to terminate processes that might be orphaned
                    # Only terminate if they are children of this Celery worker's process
                    # (this check can be complex, for simplicity we might just terminate any)
                    # A more refined check would involve parent PIDs.
                    # For safety, consider if you have other Chrome instances running.
                    proc.terminate()
                    logger.info(f"Terminated rogue {proc.info['name']} process {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process already terminated or no permission
                    pass
                except Exception as e:
                    logger.warning(f"Could not terminate {proc.info['name']} process {proc.info['pid']}: {e}")
    except ImportError:
        logger.info("psutil not available for robust process cleanup.")
    except Exception as e:
        logger.warning(f"Error during general process cleanup (psutil part): {e}")