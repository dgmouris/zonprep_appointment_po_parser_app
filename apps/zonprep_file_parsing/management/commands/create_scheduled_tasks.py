from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from apps.zonprep_file_parsing.models import ZonprepAppointment




class Command(BaseCommand):
    help = '''Create tasks that are scheduled.
    - Send Email To Fulfilment Worker.
    - Type A Email Attachment Parsing Worker
    '''

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating Tasks...")
        # Create the standard task schedule.
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.MINUTES, # for production.
            # period=IntervalSchedule.SECONDS, # for development note: remove this in the future.
        )

        # Create Task: Send Email To Fulfilment Worker
        name = "Send Email To Fulfilment Worker"
        send_out_emails_task = PeriodicTask.objects.create(
            name='Send Email To Fulfilment Worker',
            task='apps.zonprep_file_parsing.tasks.send_out_appointment_isa_emails_to_fulfillment_task',
            interval=schedule,
        )

        if send_out_emails_task:
            self.stdout.write(F"Task: '{send_out_emails_task.name}' Successfully")
        else:
            self.stdout.write(F"Task: '{name}' Creation Failed")


        # Create Task: Parsing Type A Email Attachment Worker
        name = "Parsing Type A Email Attachment Worker"
        parse_type_a_email_attachments_task = PeriodicTask.objects.create(
            name='Parsing Type A Email Attachment Worker',
            task='apps.zonprep_file_parsing.tasks.parse_type_a_email_attachments_task',
            interval=schedule,
        )

        if parse_type_a_email_attachments_task:
            self.stdout.write(F"Task: '{parse_type_a_email_attachments_task.name}' Successfully")
        else:
            self.stdout.write(F"Task: '{name}' Creation Failed")


