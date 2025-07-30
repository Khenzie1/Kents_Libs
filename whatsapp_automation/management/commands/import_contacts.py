from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import csv
import io
from whatsapp_automation.models import Contact

class Command(BaseCommand):
    help = 'Import contacts from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
    
    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                created_count = 0
                updated_count = 0
                
                for row in reader:
                    contact, created = Contact.objects.get_or_create(
                        whatsapp_name=row.get('WhatsApp Name', ''),
                        defaults={
                            'name': row.get('Name', ''),
                            'phone_number': row.get('Phone', ''),
                            'label': row.get('Label', 'WATRHC'),
                            'track': row.get('Track', ''),
                            'notes': row.get('Notes', ''),
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f"Created: {contact.name}")
                    else:
                        # Update existing contact
                        contact.name = row.get('Name', contact.name)
                        contact.phone_number = row.get('Phone', contact.phone_number)
                        contact.label = row.get('Label', contact.label)
                        contact.track = row.get('Track', contact.track)
                        contact.notes = row.get('Notes', contact.notes)
                        contact.save()
                        updated_count += 1
                        self.stdout.write(f"Updated: {contact.name}")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully imported {created_count} new contacts and updated {updated_count} existing contacts'
                    )
                )
                
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {csv_file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing contacts: {str(e)}')
            )