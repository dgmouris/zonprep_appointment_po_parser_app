from django.db import models
from django.core.exceptions import ValidationError

from apps.utils.models import BaseModel

from .state import ZonprepAppointmentState
from .gmail_utils import GmailUtility


class ZonprepAppointment(BaseModel):
    # appointment id given by the zonprep
    appointment_id = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    raw_attachment_download = models.FileField(upload_to='zonprep_appointment_attachments/', null=True, blank=True)

    def __str__(self):
        return f"{self.appointment_id} - {self.state}"


    @staticmethod
    def create_appointment(appointment_id):
        appointment, _ =ZonprepAppointment.objects.get_or_create(
            appointment_id=appointment_id,
        )
        if appointment.state == "":
            appointment.state = ZonprepAppointmentState.CREATED
            appointment.save()
        created = appointment.state == ZonprepAppointmentState.CREATED
        return appointment, created

    def get_email_subject(self):
        return F"POD for freight: {self.appointment_id}"

    # State
    '''
    This function sends out messages and will get a response from 
    parse_type_a_appointments_from_emails once the fulfillment team responds.

    fetches appointments in the CREATED state,
    sends emails out to the external fulfillment team,
    and moves the state to SENT_TO_FULFILLMENT

    Note: this will have to be in a cron job/Celery beat task.
    '''
    @staticmethod
    def move_state_to_sent_to_fulfillment():
        appointments = ZonprepAppointment.objects.filter(
            state=ZonprepAppointmentState.CREATED
        )
        for appointment in appointments:
            message = appointment.send_external_appointment_request_email()
            if message:
                appointment.state = ZonprepAppointmentState.SENT_TO_FULFILLMENT
                appointment.save()
    
    # Appointment Parser
    '''
    Parser function that will encompass the entire flow for parsing.
    '''
    @staticmethod
    def parse_type_a_appointments_from_emails():
        # fetch all records in the SENT_TO_FULFILLMENT state
        appointments = ZonprepAppointment.objects.filter(
            state=ZonprepAppointmentState.SENT_TO_FULFILLMENT
        )

        for appointment in appointments:
            # get the email hopefully returned with an attachment.
            attachment = appointment.get_type_a_appointment_email_attachment()

            # continue to the next one if there is no attachment.
            if not attachment:
                # TODO: add the day timeout to logic here explained in the state document.
                continue

            # save the email to the database.

            # parse the email

    def get_type_a_appointment_email_attachment(self):
        gmail_utils = GmailUtility()
        query_string = self.get_gmail_attachment_query_string()

        all_email = gmail_utils.search_emails(query_string, ['INBOX'])
        # if there are no emails return early.
        if not all_email:
            return


        # get the latest email with an attachment
        all_email.reverse()
        latest_email = all_email[0]

        # get message detail
        message_attachment = gmail_utils.get_message_attachment(latest_email)
        return message_attachment

    # Helper methods.
    '''
    Once the appointment is in the CREATED state
    you need to send an email to the external fulfillment

    Take a look at the save() method to see that it's going to 
    move this appointment to the next state 
    '''
    def send_external_appointment_request_email(self):
        external_fulfillment = ExternalFulfillmentEmail.load()
        gmail_utils = GmailUtility()

        subject = self.get_email_subject()
        message = gmail_utils.send_email(
            sender='steve.sheets@gmail.com',
            to=external_fulfillment.email,
            subject=subject,
            message_text=subject
        )
        return message



    def get_gmail_attachment_query_string(self):
        return F"subject:{self.get_email_subject()} has:attachment"


'''
This singleton model is solely for the purpose of storing
- external fulfillment email
'''
class SingletonModel(models.Model):
    # Define your fields here

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # If an instance of this model already exists, raise an error
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError(f"An instance of {self.__class__.__name__} already exists.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Deletion is not allowed for Singleton models.")

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

# Example usage
class ExternalFulfillmentEmail(SingletonModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self) -> str:
        return F"External fulfillment email: {self.email}"