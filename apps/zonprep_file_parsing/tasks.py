from celery import shared_task
from apps.zonprep_file_parsing.models import ZonprepAppointment
import logging

'''
NOTE (IMPORTANT):
These tasks are periodic and scheduled to run every 10 minutes.
Please referent to the file "management/commands/create_scheduled_tasks.py"

So you'll need to run
python manage.py create_scheduled_tasks

You'll also need a couple of workers to get these running:
- General worker:
celery -A zon_prep_ocr_project beat -l INFO
- Celery Beat worker
celery -A zon_prep_ocr_project worker -l INFO
(for development on windows.)
celery -A zon_prep_ocr_project worker -l INFO -P gevent
'''

@shared_task
def parse_type_a_email_attachments_task():
    logging.info("""
    ----------------------
    Parsing Emails recieved from External Fulfillment...
    """)
    ZonprepAppointment.parse_type_a_appointments_from_emails()
    logging.info("""
    ----------------------
    Complete, until next interval.
    """)


@shared_task
def send_out_appointment_isa_emails_to_fulfillment_task():
    logging.info("""
    ----------------------
    Sending out appointment ISA emails to external fulfillment...
    """)
    ZonprepAppointment.move_state_to_sent_to_fulfillment()
    logging.info("""
    ----------------------
    Complete, until next interval.
    """)
