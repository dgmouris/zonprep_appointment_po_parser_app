from datetime import datetime
import re
import time

from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from apps.utils.models import BaseModel
from apps.utils.storage import CustomGoogleCloudStorage

from .state import ZonprepAppointmentState, ZonprepPurchaseOrderState, ZonprepAppointmentTaskState
from .gmail_utils import GmailUtility
from .salesforce_utils import SalesforceUtils, SalesForceCreateError

from .file_parsers.TypeAPDFParser import TypeAPDFParser


class ZonprepAppointment(BaseModel):
    # appointment id given by the zonprep
    request_id = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    raw_attachment_download = models.FileField(
        upload_to='zonprep_appointment_attachments/',
        null=True,
        blank=True,
        storage=CustomGoogleCloudStorage()
    )
    raw_parsed_attachment_json_field = models.JSONField(null=True, blank=True)

    # this only will get triggered if you send a retry request email.
    message_send_retried = models.IntegerField(default=0)
    # needed.
    fc_code =  models.CharField(max_length=255, null=True, blank=True)
    # Note all of the parsed fields will have the prefix "p_" to denote that they are parsed fields.
    p_appointment_date = models.CharField(max_length=255, null=True, blank=True)
    p_appointment_id = models.CharField(max_length=255, null=True, blank=True)
    p_appointment_type = models.CharField(max_length=255, null=True, blank=True)
    p_carrier = models.CharField(max_length=255, null=True, blank=True)
    p_carrier_request_delivery_date = models.CharField(max_length=255, null=True, blank=True)
    p_cartons = models.CharField(max_length=255, null=True, blank=True)
    p_actual_arrival_date = models.CharField(max_length=255, null=True, blank=True)
    p_dock_door = models.CharField(max_length=255, null=True, blank=True)
    p_freight_terms = models.CharField(max_length=255, null=True, blank=True)
    p_scac = models.CharField(max_length=255, null=True, blank=True)
    p_pallets = models.CharField(max_length=255, null=True, blank=True)
    p_percent_needed = models.CharField(max_length=255, null=True, blank=True)
    p_priority_type = models.CharField(max_length=255, null=True, blank=True)
    p_trailer_number = models.CharField(max_length=255, null=True, blank=True)
    p_truck_location = models.CharField(max_length=255, null=True, blank=True)
    p_units = models.CharField(max_length=255, null=True, blank=True)

    # mapping of the fields in the "parse_appointment_pdf_to_dict" to the fields in the model.
    PARSED_FIELDS_MAPPING = {
        'Actual Arrival Date': 'p_actual_arrival_date',
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
        return f"{self.request_id} - {self.state}"

    '''
    This is the function create appointments.

    Note: don't create ZonprepAppointments another way.
    '''
    @staticmethod
    def create_appointment(appointment_id,
                           appointment_state=None,
                           fc_code=None):
        appointment, _ =ZonprepAppointment.objects.get_or_create(
            request_id=appointment_id,
        )
        if appointment_state is None:
            appointment_state = ZonprepAppointmentState.CREATED

        if appointment.state == "":
            appointment.state = appointment_state
            appointment.save()

        if fc_code is not None:
            appointment.fc_code = fc_code
            appointment.save()
        created = appointment.state == ZonprepAppointmentState.CREATED
        return appointment, created

    def get_email_subject(self):
        return F"POD for freight ISA: {self.request_id}"

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
        ZonprepAppointment.send_appointment_emails(appointments)

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
        ZonprepAppointment.process_and_parse_appointments(appointments)

    # Helper methods.
    '''
    This is the main funtion that will process all of the appointments passed in to be
    downloaded.
    '''
    @staticmethod
    def process_and_parse_appointments(appointments):
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

            # create all of the purchase orders associated with this appointment.
            appointment.create_all_pos_from_raw_parsed_fields()

            # create the appointment in salesforce
            appointment.create_appointment_in_salesforce()

            # create the purchase orders in salesforce
            appointment.create_purchase_orders_in_salesforce()

    '''
    This function will send out emails to the external fulfillment team
    and move the state to SENT_TO_FULFILLMENT
    Note: this will be used in retry logic as well.
    '''
    @staticmethod
    def send_appointment_emails(appointments):
        for appointment in appointments:
            # send the email but wait 20 seconds before sending the next one.
            time.sleep(20)
            message = appointment.send_external_appointment_request_email()
            if message:
                appointment.state = ZonprepAppointmentState.SENT_TO_FULFILLMENT
                appointment.save()

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
        # this is going to return true if successful and fail loudly if not.
        message = gmail_utils.send_email(
            to=external_fulfillment.email,
            subject=subject,
            message_text=subject
        )
        return message

    def get_gmail_attachment_query_string(self):
        # note: I only need to have the appointment id as the subject.
        return F"subject:{self.request_id} has:attachment"

    def save_raw_attachment(self, attachment_bytes):
        pdf_content = ContentFile(attachment_bytes)

        self.raw_attachment_download.save(
            F"{self.request_id}.pdf",
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
        # local read the path:
        # self.raw_attachment_download.path
        # production read the pdf file.
        pdf_file =  self.raw_attachment_download.file.read()
        type_a_pdf_parser = TypeAPDFParser(pdf_file)
        type_a_pdf_parser_dict = type_a_pdf_parser.extract_text()
        return type_a_pdf_parser_dict

    '''
    Taking the appointment raw data and saving it to the appointment model.
    '''
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
        # save computed values from the parsed fields.
        self.p_scac = self._get_scac_from_parsed_field()
        self.save()


    def _get_scac_from_parsed_field(self):
        text = self.p_carrier
        match = re.search(r"\[(.*?)\]", text)
        if match:
            result = match.group(1)
            return result
        return ""


    '''
    Taking the po raw data and creating po models from it, joined by a foreign key to this model.
    '''
    def create_all_pos_from_raw_parsed_fields(self):
        raw_all_pos_data = self.raw_parsed_attachment_json_field.get('po_data', None)
        # Note: we'll have to handle the case to differentiate between a coule
        if raw_all_pos_data is None:
            self.state = ZonprepAppointmentState.ERROR_OCR_ATTACHMENT_PARSE
            self.save()
            return

        # note that this is actually shipment data and we're going to have to
        # breakout the pos from it and create multiple from one line.
        # this is taken care of in the ZonprepPurchaseOrder.create_po_model_from_raw_po_fields method.
        for raw_po_data in raw_all_pos_data:
            ZonprepPurchaseOrder.create_po_model_from_raw_po_fields(self, raw_po_data)

    '''
    This function will send the appointment data to salesforce.
    returns
        created: bool
        success: bool
        data: dict with message and sf_appointment_id
    '''
    def create_appointment_in_salesforce(self):
        sf = SalesforceUtils()
        try:
            created, success, data = sf.create_appointment(self)
            if created and success:
                self.state = ZonprepAppointmentState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
                self.save()
                return created, data
            elif not created and success:
                self.state = ZonprepAppointmentState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
                data = {
                    "message": F"Appointment request id: {self.request_id} Already exists in salesforce",
                    "sf_appointment_id": None
                }
                self.save()
                return created, data
            else:
                self.state = ZonprepAppointmentState.ERROR_SALESFORCE_APPOINTMENT_DATA_UPLOADED
                data = {
                    "message": "Error creating appointment in salesforce",
                    "sf_appointment_id": None
                }
                return False, data
        except SalesForceCreateError as e:
            self.state = ZonprepAppointmentState.ERROR_SALESFORCE_APPOINTMENT_DATA_UPLOADED
            self.save()
            data = {
                "message": "Error creating appointment in salesforce",
                "sf_appointment_id": None
            }
            return False, data


    '''
    This function will loop through the purchase orders and add them in salesforce.
    returns: list:
        dict:
            created: bool
            success: bool
            message: str
    '''
    def create_purchase_orders_in_salesforce(self, sf_appointment_id=None):
        sf = SalesforceUtils()
        all_pos = self.purchase_orders.all()

        # values returned from the function
        return_values = []
        try:
            # create all the pos in salesforce
            result = sf.create_purchase_orders(self, sf_appointment_id)

            # loop through the results and update the state of the purchase orders.
            # the index corresponds to the index of the purchase order added in.
            for index, po in enumerate(all_pos):
                sf_result_for_po = result[index]

                if sf_result_for_po["created"] and sf_result_for_po["success"]:
                    po.state = ZonprepPurchaseOrderState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
                    po.save()
                    return_values.append({
                        "created": True,
                        "message": F"PO: {po.p_po_number} created in salesforce with id {sf_result_for_po['id']}"
                    })
                elif not sf_result_for_po["created"] and sf_result_for_po["success"]:
                    po.state = ZonprepPurchaseOrderState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
                    po.save()
                    return_values.append({
                        "created": False,
                        "message": F"PO: {po.p_po_number} already present in salesforce with id {sf_result_for_po['id']}"
                    })
                else:
                    po.state = ZonprepPurchaseOrderState.ERROR_SALESFORCE_APPOINTMENT_DATA_UPLOADED
                    po.save()
                    return_values.append({
                        "created": False,
                        "message": F"Error in creating PO: {po.p_po_number} in salesforce"
                    })
        except SalesForceCreateError as e:
            return_values.append({
                "created": False,
                "message": F"Error in creating PO: {po.p_po_number} in salesforce"
            })

        return return_values

    '''
    This function just returns emails that aren't read for a specific date.
    params:
        date: str in the format of "YYYY-MM-DD"
    returns: querySet of ZonprepAppointment
    '''
    @staticmethod
    def get_appointments_with_no_response_for_date(date):
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        appts = ZonprepAppointment.objects.filter(
            updated_at__date=date_obj,
            state__in=[
                ZonprepAppointmentState.SENT_TO_FULFILLMENT,
                ZonprepAppointmentState.FULFILLMENT_NOT_REPLIED,
            ]
        ).prefetch_related('purchase_orders')
        return appts

    '''
    This function returns any appointments that have problems with them.
    Note: *IMPORTANT" you might have to add some more when you see some more states.

    params:
        date: str in the format of "YYYY-MM-DD"
    returns
    '''
    @staticmethod
    def get_appointments_with_bad_states_for_date(date):
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        appts = ZonprepAppointment.objects.filter(
            updated_at__date=date_obj,
            state__in=[
                ZonprepAppointmentState.FULFILLMENT_RAW_ATTACHMENT_DOWNLOADED,
                ZonprepAppointmentState.INCORRECT_FULFILLMENT_ATTACHMENT_RECEIVED,
                ZonprepAppointmentState.ERROR_OCR_ATTACHMENT_PARSE,
                ZonprepAppointmentState.INVALID_ATTACHMENT,
                ZonprepAppointmentState.ERROR_SALESFORCE_APPOINTMENT_DATA_UPLOADED,
            ]
        ).prefetch_related('purchase_orders')
        return appts

class ZonprepPurchaseOrder(BaseModel):
    appointment = models.ForeignKey(
        ZonprepAppointment,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    state = models.CharField(max_length=255)

    # parsed fiels prepended with p_
    p_shipment_id = models.CharField(max_length=255, null=True, blank=True)
    p_pallets = models.CharField(max_length=255, null=True, blank=True)
    p_cartons = models.CharField(max_length=255, null=True, blank=True)
    p_units = models.CharField(max_length=255, null=True, blank=True)
    p_po_number = models.CharField(max_length=255, null=True, blank=True)
    p_pro = models.CharField(max_length=255, null=True, blank=True)
    p_bols = models.CharField(max_length=255, null=True, blank=True)
    p_asn = models.CharField(max_length=255, null=True, blank=True)
    p_arn = models.TextField(null=True, blank=True)
    p_freight_terms = models.CharField(max_length=255, null=True, blank=True)
    p_vendor = models.CharField(max_length=255, null=True, blank=True)
    p_shipment_label = models.CharField(max_length=255, null=True, blank=True)

    PARSED_FIELDS_MAPPING = {
        "shipment_id": "p_shipment_id",
        "pallets": "p_pallets",
        "cartons": "p_cartons",
        "units": "p_units",
        "pos": "p_po_number",
        "pro": "p_pro",
        "bols": "p_bols",
        "ASNs": "p_asn",
        "ARN": "p_arn",
        "freight_terms": "p_freight_terms",
        "vendor": "p_vendor",
        "shipment_label": "p_shipment_label"
    }

    def __str__(self):
        return F"PO: {self.p_po_number}, Appointment: {self.appointment}"

    '''
    This function is going to be used in the parser to create the purchase orders.

    Please take a look at parse_type_a_appointments_from_emails in the ZonprepAppointment model

    Note: don't create ZonprepPurchaseOrders another way.
    '''
    @staticmethod
    def create_po_model_from_raw_po_fields(appointment, raw_po_data):
        # note that pos is a list of numbers so we'll be creating multiple for each.
        all_pos = raw_po_data.get('pos', [""])
        # same with bols
        all_bols = raw_po_data.get('bols', [""])
        # same with asns
        all_asns = raw_po_data.get('ASNs', [""])

        # if there are no pos we're just going to skip them
        if all_pos[0] == "":
            return

        # loop through the pos and create a model for each.
        for index, po in enumerate(all_pos):
            # get the current bol or the first one if it doesn't exist.
            bol = ZonprepPurchaseOrder.get_item_or_first(all_bols, index)
            asn = ZonprepPurchaseOrder.get_item_or_first(all_asns, index)

            # this is going to map the data to the fields for the model.
            mapping = ZonprepPurchaseOrder.PARSED_FIELDS_MAPPING
            po_data = {
                mapping["shipment_id"]: raw_po_data.get("shipment_id", ""),
                mapping["pallets"]: raw_po_data.get("pallets", ""),
                mapping["cartons"]: raw_po_data.get("cartons", ""),
                mapping["units"]: raw_po_data.get("units", ""),
                mapping["pos"]: po,
                mapping["pro"]: raw_po_data.get("pro", ""),
                mapping["bols"]: bol,
                mapping["ASNs"]: asn,
                mapping["ARN"]: raw_po_data.get("ARN", ""),
                mapping["freight_terms"]: raw_po_data.get("freight_terms", ""),
                mapping["vendor"]: raw_po_data.get("vendor", ""),
                mapping["shipment_label"]: raw_po_data.get("shipment_label", "")
            }

            # unpack the data into a model.
            zonprep_purchase_order = ZonprepPurchaseOrder.objects.create(
                appointment=appointment,
                state=ZonprepPurchaseOrderState.CREATED_WITH_PARSED_FIELDS,
                **po_data
            )

            # log something here in the future.
            print(F"Created PO: {zonprep_purchase_order}")

    # Helper methods.
    @staticmethod
    def get_item_or_first(my_list, index):
        try:
            return my_list[index]
        except IndexError:
            return my_list[0]

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


class GmailTokenCredentials(SingletonModel):
    secret_credentials = models.JSONField(null=True, blank=True)
    token = models.JSONField(null=True, blank=True)
    gmail_user_id = models.CharField(max_length=255)

    def __str__(self) -> str:
        return F"Gmail User ID: {self.gmail_user_id}, Token"

    # token needs to be json.
    def update_token(self, token):
        self.token = token
        self.save()


# This is a model that will store if the task is running or not
# it will also store the last time it was run.
# it will also store the result of an error for debugging purposes
# as I want to know what the error was.
class ZonprepAppointmentTask(BaseModel):
    # there's two types of tasks that can be run
    PARSING_TYPE_A_APPOINTMENTS_TASK = "ParsingTypeAAppointments"
    SEND_APPOINTMENT_EMAILS_TASK = "SendAppointmentEmails"

    task_name = models.CharField(max_length=255)
    state = models.CharField(max_length=255) # ZonprepAppointmentTaskState
    successful = models.BooleanField(default=False, null=True, blank=True)
    error_details = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.state == ZonprepAppointmentTaskState.RUNNING:
            return F"Task: {self.task_name} State: {self.task_name}, last run started: {self.created_at}"
        return F"Task: {self.task_name} State: {self.state}, Successful: {self.successful}, last run started: {self.created_at}"

    @staticmethod
    def is_running(task_name):
        # if it doesn't exist just send them the completed state.
        existing = ZonprepAppointmentTask.objects.filter(task_name=task_name).exists()
        if not existing:
            return False
        latest_object = ZonprepAppointmentTask.objects.filter(task_name=task_name).latest('created_at')
        if latest_object:
            return latest_object.state == ZonprepAppointmentTaskState.RUNNING
        else:
            return False # there are no tasks at all.

    @staticmethod
    def set_start_task(task_name):
        ZonprepAppointmentTask.objects.create(
            task_name=task_name,
            state=ZonprepAppointmentTaskState.RUNNING
        )

    @staticmethod
    def set_end_task(task_name, successful=None, error_details=None):
        latest_object = ZonprepAppointmentTask.objects.filter(task_name=task_name).latest('created_at')
        latest_object.state = ZonprepAppointmentTaskState.COMPLETED
        latest_object.successful = successful
        latest_object.error_details = error_details
        latest_object.save()
