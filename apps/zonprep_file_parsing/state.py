'''
States are used to keep track of what step a file is in

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

CREATED = "Created"
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

STATES = {
    CREATED: CREATED,
    SENT_TO_FULFILLMENT: SENT_TO_FULFILLMENT,
    FULFILLMENT_NOT_REPLIED: FULFILLMENT_NOT_REPLIED,
    FULFILLMENT_RAW_ATTACHMENT_DOWNLOADED: FULFILLMENT_RAW_ATTACHMENT_DOWNLOADED,
    INCORRECT_FULFILLMENT_ATTACHMENT_RECEIVED: INCORRECT_FULFILLMENT_ATTACHMENT_RECEIVED,
    SUCCESSFUL_OCR_ATTACHMENT_PARSE: SUCCESSFUL_OCR_ATTACHMENT_PARSE,
    ERROR_OCR_ATTACHMENT_PARSE: ERROR_OCR_ATTACHMENT_PARSE,
    INVALID_ATTACHMENT: INVALID_ATTACHMENT,
    SUCCESSFUL_APPOINTMENT_INFO_UPDATED: SUCCESSFUL_APPOINTMENT_INFO_UPDATED,
    SUCCESSFUL_APPOINTMENT_PO_DATA_CREATED: SUCCESSFUL_APPOINTMENT_PO_DATA_CREATED,
    SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED: SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED,
    ERROR_SALESFORCE_APPOINTMENT_DATA_UPLOADED: ERROR_SALESFORCE_APPOINTMENT_DATA_UPLOADED,
}
