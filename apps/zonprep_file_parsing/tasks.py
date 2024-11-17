from celery import shared_task
from apps.zonprep_file_parsing.models import (ZonprepAppointment,
                                              ZonprepPurchaseOrder,
                                              ZonprepAppointmentTask)
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

@shared_task(queue="parsing_queue")
def parse_type_a_email_attachments_task():
    logging.info("""
    ----------------------
    Parsing Emails recieved from External Fulfillment Task...
    """)
    # check to see if the task is running
    task_name = ZonprepAppointmentTask.PARSING_TYPE_A_APPOINTMENTS_TASK
    is_running = ZonprepAppointmentTask.is_running(task_name)
    if is_running:
        logging.info("Task is already running, skipping...")
        return
    # run the task.
    ZonprepAppointmentTask.set_start_task(task_name)
    successful = True
    error_details = ""
    try:
        logging.info("Running task...")
        ZonprepAppointment.parse_type_a_appointments_from_emails()
    except Exception as error:
        successful = False
        error_details = F"{error}"
        logging.error(f"Error: {error}")
    ZonprepAppointmentTask.set_end_task(task_name, successful=successful, error_details=error_details)
    logging.info("""
    Complete, until next interval.
    ----------------------
    """)

@shared_task(queue="parsing_queue_type_c")
def parse_type_c_email_attachments_task():
    logging.info("""
    ----------------------
    Parsing Emails recieved from External Fulfillment Task...
    """)
    # check to see if the task is running
    task_name = ZonprepAppointmentTask.PARSING_TYPE_C_APPOINTMENTS_TASK
    is_running = ZonprepAppointmentTask.is_running(task_name)
    if is_running:
        logging.info("Task is already running, skipping...")
        return
    # run the task.
    ZonprepAppointmentTask.set_start_task(task_name)
    successful = True
    error_details = ""
    try:
        logging.info("Running task...")
        # ZonprepAppointment.parse_type_c_appointments_from_emails()
        ZonprepPurchaseOrder.parse_type_c_purchase_orders_from_emails()
    except Exception as error:
        successful = False
        error_details = F"{error}"
        logging.error(f"Error: {error}")
    ZonprepAppointmentTask.set_end_task(task_name, successful=successful, error_details=error_details)
    logging.info("""
    Complete, until next interval.
    ----------------------
    """)



@shared_task(queue="email_queue")
def send_out_appointment_isa_emails_to_fulfillment_task():
    logging.info("""
    ----------------------
    Sending out appointment ISA emails to external fulfillment...
    """)
    # check to see if the task is running
    task_name = ZonprepAppointmentTask.SEND_APPOINTMENT_EMAILS_TASK
    is_running = ZonprepAppointmentTask.is_running(task_name)
    if is_running:
        logging.info("Task is already running, skipping...")
        return
    # run the task.
    ZonprepAppointmentTask.set_start_task(task_name)
    successful = True
    error_details = ""
    try:
        logging.info("Running task...")
        ZonprepAppointment.move_state_to_sent_to_fulfillment()
    except Exception as error:
        successful = False
        error_details = F"{error}"
        logging.error(f"Error: {error}")
    ZonprepAppointmentTask.set_end_task(task_name, successful=successful, error_details=error_details)
    logging.info("""
    Complete, until next interval.
    ----------------------
    """)

