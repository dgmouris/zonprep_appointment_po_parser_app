from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from apps.utils.models import BaseModel

from .state import ZonprepAppointmentState
from .gmail_utils import GmailUtility

from .file_parsers.TypeAPDFParser import TypeAPDFParser


class ZonprepAppointment(BaseModel):
    # appointment id given by the zonprep
    appointment_id = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    raw_attachment_download = models.FileField(upload_to='zonprep_appointment_attachments/', null=True, blank=True)
    raw_parsed_attachment_json_field = models.JSONField(null=True, blank=True)

    # Note all of the parsed fields will have the prefix "p_" to denote that they are parsed fields.
    p_appointment_date = models.CharField(max_length=255, null=True, blank=True)
    p_appointment_id = models.CharField(max_length=255, null=True, blank=True)
    p_appointment_type = models.CharField(max_length=255, null=True, blank=True)
    p_carrier = models.CharField(max_length=255, null=True, blank=True)
    p_carrier_request_delivery_date = models.CharField(max_length=255, null=True, blank=True)
    p_cartons = models.CharField(max_length=255, null=True, blank=True)
    p_dock_door = models.CharField(max_length=255, null=True, blank=True)
    p_freight_terms = models.CharField(max_length=255, null=True, blank=True)
    p_pallets = models.CharField(max_length=255, null=True, blank=True)
    p_percent_needed = models.CharField(max_length=255, null=True, blank=True)
    p_priority_type = models.CharField(max_length=255, null=True, blank=True)
    p_trailer_number = models.CharField(max_length=255, null=True, blank=True)
    p_truck_location = models.CharField(max_length=255, null=True, blank=True)
    p_units = models.CharField(max_length=255, null=True, blank=True)

    # mapping of the fields in the "raw_parsed_attachment_json_field" to the fields in the model.
    PARSED_FIELDS_MAPPING = {
        'Actual Arrival Date': 'p_appointment_date',
        'Appointment Id': 'p_appointment_id',
        'Appointment type': 'p_appointment_type',
        'Carrier': 'p_carrier',
        'Carrier request delivery time and date': 'p_carrier_request_delivery_date',
        'Cartons': 'p_cartons',
        'Dock Door': 'p_dock_door',
        'Freight terms': 'p_freight_terms',
        'Pallets': 'p_pallets',
        'Percent needed': 'p_percent_needed',
        'Priority type': 'p_priority_type',
        'Schedule Date': 'p_appointment_date',
        'Trailer Number': 'p_trailer_number',
        'Truck location': 'p_truck_location',
        'Units': 'p_units'
    }

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

    Note: this will have to be in a cron job/Celery beat task.
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
            appointment.save_raw_attachment(attachment)

            # move the state to FULFILLMENT_RAW_ATTACHMENT_DOWNLOADED
            appointment.state = ZonprepAppointmentState.FULFILLMENT_RAW_ATTACHMENT_DOWNLOADED
            appointment.save()

            # parse the email attachement and set the state to SUCCESSFUL_OCR_ATTACHMENT_PARSE
            parsed_appointment_pdf_data = appointment.parse_appointment_pdf_to_dict()                        
            appointment.raw_parsed_attachment_json_field = parsed_appointment_pdf_data
            appointment.state = ZonprepAppointmentState.SUCCESSFUL_OCR_ATTACHMENT_PARSE
            appointment.save()

            # convert the and move the the state to SUCCESSFUL_APPOINTMENT_INFO_UPDATED
            appointment.save_raw_parsed_appointment_fields_to_model()

            # TODO: send the appointment data to salesforce
            appointment.send_appointment_data_to_salesforce()

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

    def save_raw_attachment(self, attachment_bytes):
        pdf_content = ContentFile(attachment_bytes)

        self.raw_attachment_download.save(
            F"{self.appointment_id}.pdf",
            pdf_content
        )

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

        # note that this is going to be in bytes.
        return message_attachment

    def parse_appointment_pdf_to_dict(self):
        type_a_pdf_parser = TypeAPDFParser(self.raw_attachment_download.path)
        type_a_pdf_parser_dict = type_a_pdf_parser.extract_text()
        return type_a_pdf_parser_dict

    def save_raw_parsed_appointment_fields_to_model(self):
        appointment_data = self.raw_parsed_attachment_json_field.get('appointment_data', None)
        # handle the case if it's not saved correctly.
        if appointment_data is None:
            self.state = ZonprepAppointmentState.ERROR_OCR_ATTACHMENT_PARSE
            self.save()
            return
        # loop through the mapping and set the fields in the model.
        for key, value in appointment_data.items():
            if key in self.PARSED_FIELDS_MAPPING:
                field_name = self.PARSED_FIELDS_MAPPING[key]
                setattr(self, field_name, value)
        self.state = ZonprepAppointmentState.SUCCESSFUL_APPOINTMENT_INFO_UPDATED
        self.save()

    '''
    This function will send the appointment data to salesforce.
    '''
    def send_appointment_data_to_salesforce(self):
        pass


'''
This singleton model is solely for the purpose of storing
- external fulfillment email
'''
class SingletonModel(models.Model):
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