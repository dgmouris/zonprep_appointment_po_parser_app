from enum import Enum


class ZonprepAppointmentTaskState(Enum):
    RUNNING = "Running"
    COMPLETED = "Completed"

    def __str__(self):
        return self.value


class ZonprepAppointmentState(Enum):
    CREATED = "Created"
    DELETED = "Deleted"
    SENT_TO_FULFILLMENT = "SentToFulfillment"
    FULFILLMENT_NOT_REPLIED = "FulfillmentNotReplied"
    FULFILLMENT_RAW_ATTACHMENT_DOWNLOADED = "FulfillmentRawAttachmentDownloaded"
    INCORRECT_FULFILLMENT_ATTACHMENT_RECEIVED = "IncorrectFulfillmentAttachmentRecieved"
    SUCCESSFUL_OCR_ATTACHMENT_PARSE = "SuccessfulOCRAttachmentParse"
    ERROR_OCR_ATTACHMENT_PARSE = "ErrorOCRAttachmentParse"
    INVALID_ATTACHMENT = "InvalidAttachment"
    SUCCESSFUL_APPOINTMENT_INFO_UPDATED = "SuccessfulAppointmentInfoUpdated"
    SUCCESSFUL_APPOINTMENT_PO_DATA_CREATED = "SuccessfulAppointmentPODataCreated"
    SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED = "SuccessSalesforceAppointmentDataUploaded"
    ERROR_SALESFORCE_APPOINTMENT_DATA_UPLOADED = "ErrorSalesforceAppointmentDataUploaded"

    def __str__(self):
        return self.value

class ZonprepPurchaseOrderState(Enum):
    CREATED_WITH_PARSED_FIELDS = "CreatedWithParsedFields"
    SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED = "SuccessSalesforceAppointmentDataUploaded"
    ERROR_SALESFORCE_APPOINTMENT_DATA_UPLOADED = "ErrorSalesforceAppointmentDataUploaded"
    # everything below this line is for the TypeC Image parsing.
    SCHEDULED_TO_SEND_TO_FULFILLMENT = "ScheduledToSendToFulfillment"
    SENT_TO_FULFILLMENT_FOR_PO_SKU = "SentToFulfillmentForSKU"
    FULFILLMENT_NOT_REPLIED_FOR_PO_SKU = "FulfillmentNotRepliedForSKU"
    FULFILLMENT_RAW_ATTACHMENT_DOWNLOADED_FOR_PO_SKU = "FulfillmentRawAttachmentDownloadedForSKU"
    INCORRECT_FULFILLMENT_ATTACHMENT_RECEIVED_FOR_PO_SKU = "IncorrectFulfillmentAttachmentRecievedForSKU"
    SUCCESSFUL_OCR_ATTACHMENT_PARSE_FOR_PO_SKU = "SuccessfulOCRAttachmentParseForSKU"
    ERROR_OCR_ATTACHMENT_PARSE_FOR_PO_SKU = "ErrorOCRAttachmentParseForSKU"
    INVALID_ATTACHMENT_FOR_PO_SKU = "InvalidAttachmentForSKU"
    SUCCESSFUL_PO_SKU_DATA_CREATED = "SuccessfulAppointmentPODataCreatedForSKU"
    SUCCESS_SALESFORCE_PO_SKU_DATA_UPLOADED = "SuccessSalesforceAppointmentDataUploaded"
    ERROR_SALESFORCE_PO_SKU_DATA_UPLOADED = "ErrorSalesforceAppointmentDataUploaded"

    def __str__(self):
        return self.value

'''
Notes on the above.
States are used to keep track of what step an appointment is in.

- Created
Record created in the upload appointments
flow but not sent.
- SentToFulfillment
This record has be extenally sent but not
but not received yet.
- FulfillmentNotReplied
This is a record that was in the state
"SentToFulfillment" but not replied in the
last 30 days (something to talk about
with Zonprep) how do we want to deal
with timeouts.
- FulfillmentRawAttachmentDownloaded
This is a record that has read the email,
downloaded the attachment to some sort
of storage device.
- IncorrectFulfullmentAttachmentRecieved
This is a record that has read the email
and there is an attachment
- SuccessfulOCRAttachmentParse
This means that the data has been parsed
and the JSON data has been taken from the
document.
- ErrorOCRAttachmentParse
This is going to be that the document has cause
- InvalidAttachment
This is going to be the state of the documents
that we'll want to ignore in our statistics
- SuccessfulAppointmentInfoUpdated
This is going to mean the Appointment info has
been saved to the database.
- SuccessfulAppointmentPODataCreated
this is going to mean that the POs have been
created from the appointment.
- SuccessSalesforceAppointmentDataUploaded
this is going to be an appointment that has
all of the data uploaded data to salesforce
- ErrorSalesforceAppointmentDataUploaded
an error has occurred and we'll have to do something
with these probably manually at some point.

'''
