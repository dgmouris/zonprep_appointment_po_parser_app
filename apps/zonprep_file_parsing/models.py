from datetime import datetime
import re
import time
import logging
from io import BytesIO
from PIL import Image

from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from apps.utils.models import BaseModel
from apps.utils.storage import CustomGoogleCloudStorage

from .state import ZonprepAppointmentState, ZonprepPurchaseOrderState, ZonprepAppointmentTaskState
from .gmail_utils import GmailUtility
from .salesforce_utils import SalesforceUtils, SalesForceCreateError

from .file_parsers.TypeAPDFParser import TypeAPDFParser
from .file_parsers.TypeCImageParser import TypeCImageParser

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
        )[:400]
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
        ).order_by('?')[:400]
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
            time.sleep(9)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.info(F"Sent email for {current_time}")
            message = appointment.send_external_appointment_request_email()
            print(F"Sent email for {current_time}")
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

    # fields for the image parsing and sku creation.
    raw_parsed_attachment_json_field = models.JSONField(null=True, blank=True)


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
        return F"PO: {self.p_po_number} - {self.state}, Appointment: {self.appointment}"

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

    # State functions

    # move the state to send this to the fulfilment team.
    # note this will be unique to the purchase order.
    def move_state_to_scheduled_to_send_to_fulfillment(self):
        self.state = ZonprepPurchaseOrderState.SCHEDULED_TO_SEND_TO_FULFILLMENT
        self.save()

    '''
    This functions sends out Purchase Order emails to the external fulfillment team

    fetches purchase orders in the SCHEDULED_TO_SEND_TO_FULFILLMENT state,
    sends emails out to the external fulfillment team,
    and moves the state to SENT_TO_FULFILLMENT_FOR_PO_SKU

    Note: this will have to be in a cron job/Celery beat task.
    '''
    @staticmethod
    def move_state_to_sent_to_fulfillment():
        purchase_orders = ZonprepPurchaseOrder.objects.filter(
            state= ZonprepPurchaseOrderState.SCHEDULED_TO_SEND_TO_FULFILLMENT
        )[:200]
        ZonprepPurchaseOrder.send_purchase_order_emails(purchase_orders)

    # Purchase Order Parser
    @staticmethod
    def parse_type_c_purchase_orders_from_emails():
        purchase_orders = ZonprepPurchaseOrder.objects.filter(
            state=ZonprepPurchaseOrderState.SENT_TO_FULFILLMENT_FOR_PO_SKU
        ).prefetch_related("image_attachments")[:200]

        ZonprepPurchaseOrder.process_and_parse_purchase_orders(purchase_orders)

    # Helper methods.
    @staticmethod
    def process_and_parse_purchase_orders(purchase_orders):
        for po in purchase_orders:
            print(F"Processing PO: {po.p_po_number}")
            # get the email hopefully returned with an attachment.
            attachment = po.get_type_c_purchase_order_email_attachment()
            # continue to the next one if there is no attachment.

            # check to make sure that the attachment is the correct one.
            if not attachment:
                # TODO: add the day timeout logic.
                continue

            if  po.image_attachments.all().exists():
                # delete the old attachment.
                po.image_attachments.all().delete()
            # save the attachment to the database.
            po.save_image_attachment(attachment)

            # move the state to FULFILLMENT_RAW_ATTACHMENT_DOWNLOADED
            po.state = ZonprepPurchaseOrderState.FULFILLMENT_RAW_ATTACHMENT_DOWNLOADED_FOR_PO_SKU
            po.save()

            # parse the email attachement and set the state to SUCCESSFUL_OCR_ATTACHMENT_PARSE
            po_sku_data = po.parse_purchase_order_image_attachment()
            po.raw_parsed_attachment_json_field = po_sku_data
            po.state = ZonprepPurchaseOrderState.SUCCESSFUL_OCR_ATTACHMENT_PARSE_FOR_PO_SKU
            po.save()

            # convert the and move the the state to SUCCESSFUL_PO_SKU_DATA_CREATED
            try:
                po.create_all_po_skus_from_raw_parsed_fields()
                po.state = ZonprepPurchaseOrderState.SUCCESSFUL_PO_SKU_DATA_CREATED
                po.save()
            except Exception as e:
                po.state = ZonprepPurchaseOrderState.ERROR_OCR_ATTACHMENT_PARSE_FOR_PO_SKU
                po.save()

            # this is going to be where I send all of the po skus to salesforce.

    def create_all_po_skus_from_raw_parsed_fields(self):
        sku_data = self._get_formatted_po_skus_data_from_raw_parsed_fields()

        # all_mapped_sku_data = self.create_all_po_skus_from_raw_parsed_fields()
        for mapped_sku_data in sku_data:
            ZonprepPurchaseOrderSKU.create_po_sku_model_from_raw_po_sku_fields(self, mapped_sku_data)

    # read through the raw parsed fields and ensure they are saved correctly
    '''
        The data from the above will be 3 rows in total for each sku
        - row 1:
            cols_0 to cols_9 or cols_10
            - have most of the data.
        - row 2: last to match col with x_min and x_max
            cols_0
                - units for last cols_3 of last row
            cols_1
                - date for cols_
            cols_2
                - date
        - row 3
            prep details which will be it's own thing.
    '''
    def _get_formatted_po_skus_data_from_raw_parsed_fields(self):
        current_row = None
        # this is going to create a set of inval
        in_valid_col_values = {
            "fnsku",
            "iaid",
            "eastern time"
        }

        data_mapping = {
            "fnsku": {
                "x_coordinates": None,
                "multi_line": False,
                "anchor": "left",
                "col_from_anchor": 0,
            },
            "iaid": {
                "x_coordinates": None,
                "multi_line": False,
                "anchor": "left",
                "col_from_anchor": 1,
            },
            "msku": {
                "x_coordinates": None,
                "multi_line": True,
                "anchor": "left",
                "col_from_anchor": 2,
            },
            "weight": {
                "x_coordinates": None,
                "multi_line": True,
                "anchor": "left",
                "col_from_anchor": 3,
            },
            "quantity": {
                "x_coordinates": None,
                "multi_line": False,
                "anchor": "left",
                "col_from_anchor": 4,
            },
            "create_date": {
                "x_coordinates": None,
                "multi_line": True,
                "anchor": "right",
                "col_from_anchor": 1,
            },
            "update_date": {
                "x_coordinates": None,
                "multi_line": True,
                "anchor": "right",
                "col_from_anchor": 0,
            },
        }

        all_mapped_sku_data = []

        for row_index, sku_data_row in enumerate(self.raw_parsed_attachment_json_field):

            col_values_only = [col["value"].lower() for col in sku_data_row.values()]
            col_values_only_set = set(col_values_only)
            # check to see if if there's intersection with bad values
            intersection_of_invalid_cols = in_valid_col_values.intersection(col_values_only_set)
            # if there are any invalid columns then we're going to skip this row.
            if (len(list(intersection_of_invalid_cols)) > 0
                and current_row is None):
                continue

            # check if the columns are less than 7 and than 11 then we should skip them.
            # this is the sweet spot of columns.
            if len(col_values_only) < 7 or len(col_values_only) > 11:
                # this is the first row or invalid rows so skip them.
                # the prep
                continue

            current_row = sku_data_row
            next_row = ZonprepPurchaseOrder.get_next_row(
                self.raw_parsed_attachment_json_field,
                row_index ,
            )
            mapped_sku_data = {}
            # PART 1: Handle the row with most of the data in it that's not prep details.
            for mapping_col, mapping_value in data_mapping.items():
                # get the x coordinates
                x_coordinates = mapping_value["x_coordinates"]
                # get the anchor
                anchor = mapping_value["anchor"]
                # get the column from the anchor
                col_from_anchor = mapping_value["col_from_anchor"]
                # get the multi line
                multi_line = mapping_value["multi_line"]

                # get the raw parsed data column based on the read anchor (left or right)
                raw_parsed_data_col = ""
                if anchor == "left":
                    raw_parsed_data_col = F"cols_{col_from_anchor}"
                if anchor == "right":
                    raw_parsed_data_col = F"cols_{len(current_row) - col_from_anchor - 1}"

                current_col = current_row[raw_parsed_data_col]
                # update the x coordinates if they don't exist for anchors.
                if x_coordinates is None:
                    data_mapping[mapping_col]["x_coordinates"] = [current_col["x_min"], current_col["x_max"]]

                # get the value from the next row if it's multi line.
                # check if it's aligned with the 0 x coordinate from the current_row
                next_row_value = ""
                if multi_line:
                    PIXEL_TOLERANCE = 20
                    for next_row_col, next_row_mapping in next_row.items():
                        # check that it's within the pixel tolerance within the x_min.
                        if (next_row_mapping["x_min"] <= current_col["x_min"] + PIXEL_TOLERANCE and
                            next_row_mapping["x_min"] >= current_col["x_min"] - PIXEL_TOLERANCE):
                            # set the next row value

                            next_row_value = next_row[next_row_col]["value"]
                            break

                # update the value
                mapped_sku_data[mapping_col] = F"{current_col['value']} {next_row_value}".strip()

            # PART 2: Handle the prep details row.
            prep_details_row = ZonprepPurchaseOrder.get_next_row(
                self.raw_parsed_attachment_json_field,
                row_index + 1,
            )
            prep_details_row_more = ZonprepPurchaseOrder.get_next_row(
                self.raw_parsed_attachment_json_field,
                row_index + 2,
            )
            # get the prep details value if it's upper case or not.
            prep_details_value = ZonprepPurchaseOrder.get_prep_details_value(
                prep_details_row,
                prep_details_row_more
            )

            # if it's empty there was an issue, just add the data and move on.
            if prep_details_value.strip() == "":
                all_mapped_sku_data.append(mapped_sku_data)
                continue

            # this prep_details_value string normally takes the value of the following:
            # 'PREP DETAILS: ITEM_LABELING: {OWNER: MERCHANT, COST OWNER: NOT_APPLICABLE }'
            # this is going to be formatted into a dictionary.
            formatted_prep_details_data = ZonprepPurchaseOrder.format_prep_details_from_raw_string(prep_details_value)

            # add the formatted_prep_details_data to the mapped_sku_data
            for formatted_prep_details in formatted_prep_details_data:
                mapped_sku_data = {**mapped_sku_data, **formatted_prep_details}
            mapped_sku_data["all_prep_details"] = formatted_prep_details_data
            all_mapped_sku_data.append(mapped_sku_data)

        return all_mapped_sku_data

    @staticmethod
    def strip_all_weird_characters(data):
        return data.replace("_", " ").replace("{", "").replace("}", "").strip()

    # format prep details so it's digestable
    @staticmethod
    def format_prep_details_from_raw_string(prep_details_string):
        # you're going to get a string like this:
        # 'Prep details: ITEM_LABELING: {Owner: MERCHANT, Cost owner: NOT_APPLICABLE }, ITEM_POLYBAGGING: {Owner: MERCHANT, Cost owner: NOT_APPLICABLE }'

        # this is going to look like ['Owner: MERCHANT, Cost owner: NOT_APPLICABLE ', 'Owner: MERCHANT, Cost owner: NOT_APPLICABLE ']
        owner_details = re.findall(r'\{([^}]+)\}', prep_details_string)
        # this is going to give a list that looks like ['item_labeling', ' item_polybagging']
        prep_details_titles = re.sub(
                r'\{([^}]+)\}', '', prep_details_string
            ).lower(
            ).replace(
            "prep details:", ""
            ).replace(
            ":", ""
            ).strip(
            ).split(",")

        # going to make an array of these values until I know how to handle them.
        formatted_prep_details = []
        for index in range(len(prep_details_titles)):
            key_prepended =F"prep_details_{prep_details_titles[index].strip()}"
            owner, cost_owner = owner_details[index].split(",")
            formatted_prep_details.append({
                F"{key_prepended}": prep_details_titles[index].strip(),
                F"{key_prepended}_owner": owner.strip(),
                F"{key_prepended}_cost_owner": cost_owner.strip()
            })
        return formatted_prep_details

    # this will return the first column or just ignore the data
    # this is needed
    @staticmethod
    def get_prep_details_value(prep_details_row_one, prep_details_row_two):
        # get the first
        first_row = " ".join(
            [value["value"] for value in prep_details_row_one.values()]
        ).strip()
        # if it ends with } it's probably somthing like "Prep details: ITEM_LABELING: {Owner: MERCHANT, Cost owner: NOT_APPLICABLE }"
        if first_row.endswith("}"):
            return first_row

        second_row = " ".join(
            [value["value"] for value in prep_details_row_two.values()]
        ).strip()

        return F"{first_row} {second_row}".strip()

    @staticmethod
    def get_next_row(data, index):
        try:
            return data[index + 1]
        except IndexError:
            return []

    def parse_purchase_order_image_attachment(self):
        # get the image attachment
        image_attachment = self.image_attachments.first()
        if not image_attachment:
            return None
        # get the image attachment bytes
        image_attachment_bytes = image_attachment.image_attachment.read()
        # parse the images.
        type_c_image_parser = TypeCImageParser(image_attachment_bytes)
        po_sku_data = type_c_image_parser.extract_text()
        return po_sku_data


    def get_type_c_purchase_order_email_attachment(self):
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

    def get_gmail_attachment_query_string(self):
        # note: I only need to have the appointment id as the subject.
        return F"subject:{self.p_po_number} has:attachment"

    def save_image_attachment(self, attachment_bytes):
        # image_content = ContentFile(attachment_bytes)
        attachment_instance = ZonprepPOImageAttachments.save_image_attachment(self, attachment_bytes)
        return attachment_instance

    '''
    This function will send out emails to the external fulfillment team
    and move the state to SENT_TO_FULFILLMENT
    Note: this will be used in retry logic as well.
    '''
    @staticmethod
    def send_purchase_order_emails(purchase_orders):
        for po in purchase_orders:
            # send the email but wait 20 seconds before sending the next one.
            time.sleep(9)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.info(F"Sent email for {current_time}")
            message = po.send_external_purchase_order_request_email()
            print(F"Sent email for {current_time}")
            if message:
                po.state = ZonprepPurchaseOrderState.SENT_TO_FULFILLMENT_FOR_PO_SKU
                po.save()

    # this is only going to send the email and not perform the state change.
    def send_external_purchase_order_request_email(self):
        external_fulfillment = ExternalFulfillmentEmail.load()
        gmail_utils = GmailUtility()

        subject = self.get_email_subject()
        message_text = self.get_message_text()
        # this is going to return true if successful and fail loudly if not.
        message = gmail_utils.send_email(
            to=external_fulfillment.email,
            subject=subject,
            message_text=message_text
        )
        return message

    def get_email_subject(self):
        return F"PO Shipments Items for: {self.p_po_number}"

    def get_message_text(self):
        return F"""
        for the  PO: {self.p_po_number} please return table view containing data:
        - fnsku
        - iaid
        - msku
        - weight
        - shipped quantity
        - recieved quantity
        - update date
        - create date
        - prep details
        """

    @staticmethod
    def get_item_or_first(my_list, index):
        try:
            return my_list[index]
        except IndexError:
            return my_list[0]

class ZonprepPOImageAttachments(BaseModel):
    purchase_order = models.ForeignKey(
        ZonprepPurchaseOrder,
        on_delete=models.CASCADE,
        related_name='image_attachments'
    )
    image_attachment = models.FileField(
        upload_to='zonprep_po_image_attachments/',
        null=True,
        blank=True,
        storage=CustomGoogleCloudStorage()
    )
    raw_parsed_attachment_json_field = models.JSONField(null=True, blank=True)


    # SCALE FACTOR FOR IMAGE RESIZING
    SCALE_FACTOR = 2.0

    def __str__(self):
        return F"PO Image Attachment: {self.purchase_order.p_po_number}"

    '''
    This will change when we have multiple images for a purchase order.
    '''
    @staticmethod
    def save_image_attachment(purchase_order, attachment_bytes):
        # do a check if there's already an attachment in the future.

        # first handle the single file case.
        file_name= F"{purchase_order.p_po_number}_image_0.png"
        image_content = ContentFile(
            attachment_bytes,
            name = file_name
        )

        resized_image_content = ZonprepPOImageAttachments.resize_content_file(image_content)

        po_attachment = ZonprepPOImageAttachments(
            purchase_order=purchase_order
        )

        po_attachment.image_attachment.save(
            file_name,
            resized_image_content
        )
        po_attachment.save()
        return po_attachment

    @staticmethod
    def resize_content_file(content_file):
        # Use ContentFile as a file-like object
        image = Image.open(content_file)

        scale_factor = ZonprepPOImageAttachments.SCALE_FACTOR
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)
        # Perform operations on the image (e.g., resizing)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)  # Resize to 200x200 pixels for example
        # Save the modified image to a new ContentFile
        new_image_io = BytesIO()
        resized_image.save(new_image_io, format="PNG")
        new_content_file = ContentFile(new_image_io.getvalue(), name=image.filename)

        return new_content_file


class ZonprepPurchaseOrderSKU(BaseModel):
    purchase_order = models.ForeignKey(
        ZonprepPurchaseOrder,
        on_delete=models.CASCADE,
        related_name='skus'
    )

    # parsed fields prepended with p_
    # anchored left to right in the parsing.
    p_fnsku = models.CharField(max_length=255, null=True, blank=True)
    p_iaid = models.CharField(max_length=255, null=True, blank=True)
    p_msku = models.CharField(max_length=255, null=True, blank=True)
    p_weight = models.CharField(max_length=255, null=True, blank=True) # multi line in parsing.
    p_shipped_quantity = models.CharField(max_length=255, null=True, blank=True)
    p_recieved_quantity = models.CharField(max_length=255, null=True, blank=True)

    # anchored right to left in parsing
    p_update_date = models.CharField(max_length=255, null=True, blank=True)
    p_create_date = models.CharField(max_length=255, null=True, blank=True)

    # fields for prep details which is its' own line.
    p_prep_details_item_labelling = models.CharField(max_length=255, null=True, blank=True)
    p_prep_details_item_labelling_owner = models.CharField(max_length=255, null=True, blank=True)
    p_prep_details_item_labelling_cost_owner = models.CharField(max_length=255, null=True, blank=True)
    p_prep_details_polybagging = models.CharField(max_length=255, null=True, blank=True)
    p_prep_details_polybagging_owner = models.CharField(max_length=255, null=True, blank=True)
    p_prep_details_polybagging_cost_owner = models.CharField(max_length=255, null=True, blank=True)
    p_all_prep_details = models.JSONField(null=True, blank=True)

    def __str__(self):
        return F"SKU: {self.p_fnsku} for PO: {self.purchase_order.p_po_number}"

    @staticmethod
    def create_po_sku_model_from_raw_po_sku_fields(purchase_order, mapped_po_sku_data):
        SKU_PARSED_FIELDS_MAPPING = {
            "fnsku": "p_fnsku",
            "iaid": "p_iaid",
            "msku": "p_msku",
            "weight": "p_weight",
            "quantity": "p_shipped_quantity",
            "create_date": "p_create_date",
            "update_date": "p_update_date",
            "prep_details_item_labeling": "p_prep_details_item_labelling",
            "prep_details_item_labeling_owner": "p_prep_details_item_labelling_owner",
            "prep_details_item_labeling_cost_owner": "p_prep_details_item_labelling_cost_owner",
            "prep_details_item_polybagging": "p_prep_details_polybagging",
            "prep_details_item_polybagging_owner": "p_prep_details_polybagging_owner",
            "prep_details_item_polybagging_cost_owner": "p_prep_details_polybagging_cost_owner",
            "all_prep_details": "p_all_prep_details",
        }
        # create the model data.
        po_sku_model_data = { SKU_PARSED_FIELDS_MAPPING[key]: value
                             for key, value in mapped_po_sku_data.items()
                             if key in SKU_PARSED_FIELDS_MAPPING}

        po_sku =  ZonprepPurchaseOrderSKU.objects.create(
            purchase_order=purchase_order,
            **po_sku_model_data
        )

        print(F"Created PO SKU: {po_sku}")

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
