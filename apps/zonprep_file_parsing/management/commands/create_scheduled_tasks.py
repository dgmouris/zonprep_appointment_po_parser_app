from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from django.conf import settings


class Command(BaseCommand):
    help = '''Create tasks that are scheduled.
    - Send Email To Fulfilment Worker.
    - Type A Email Attachment Parsing Worker
    '''

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating Tasks...")
        # Create the standard task schedule
        # shorter interval for development.
        schedule = None
        if settings.DEBUG:
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=10,
                period=IntervalSchedule.SECONDS, # for development note: remove this in the future.
            )
        else:
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=5,
                period=IntervalSchedule.MINUTES, # for production.
            )
        
        # Create Task: Send Email To Fulfilment Worker
        name = "Send Email To Fulfilment Worker"
        
        already_exists = self._does_task_exist(name)
        
        if not already_exists:
            send_out_emails_task = PeriodicTask.objects.create(
                name='Send Email To Fulfilment Worker',
                task='apps.zonprep_file_parsing.tasks.send_out_appointment_isa_emails_to_fulfillment_task',
                interval=schedule,
            )

            if send_out_emails_task:
                self.stdout.write(F"Task: '{send_out_emails_task.name}' Successfully")
            else:
                self.stdout.write(F"Task: '{name}' Creation Failed")
        else:
            self.stdout.write(F"Task: '{name}' Already Exists, nothing to do.")

        # Create Task: Parsing Type A Email Attachment Worker
        name = "Parsing Type A Email Attachment Worker"
        
        already_exists = self._does_task_exist(name)
        if not already_exists:
            parse_type_a_email_attachments_task = PeriodicTask.objects.create(
                name='Parsing Type A Email Attachment Worker',
                task='apps.zonprep_file_parsing.tasks.parse_type_a_email_attachments_task',
                interval=schedule,
            )

            if parse_type_a_email_attachments_task:
                self.stdout.write(F"Task: '{parse_type_a_email_attachments_task.name}' Successfully")
            else:
                self.stdout.write(F"Task: '{name}' Creation Failed")
        else:
            self.stdout.write(F"Task: '{name}' Already Exists, nothing to do.")


    def _does_task_exist(self, task_name):
        return PeriodicTask.objects.filter(name=task_name).exists()