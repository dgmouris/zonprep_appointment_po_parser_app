import React from 'react'

import Badge from '@/components/utils/uikit/Badge'

const STATE_MAPPING = {
  "CreatedWithParsedFields": {
    color: "yellow",
    text: "ParseFields"
  },
  "SuccessSalesforceAppointmentDataUploaded": {
    color: "green",
    text: "Data Saved"
  },
  "ErrorSalesforceAppointmentDataUploaded": {
    color: "red",
    text: "Data Error"
  },
  "ScheduledToSendToFulfillment": {
    color: "green",
    text: "Queued to be Sent"
  },
  "SentToFulfillmentForSKU": {
    color: "indigo",
    text: "Sent to Fulfillment"
  },
  "FulfillmentNotRepliedForSKU": {
    color: "red",
    text: "No Reply"
  },
  "FulfillmentRawAttachmentDownloadedForSKU": {
    color: "yellow",
    text: "Attachment Downloaded"
  },
  "IncorrectFulfillmentAttachmentRecievedForSKU": {
    color: "red",
    text: "Incorrect Attachment"
  },
  "SuccessfulOCRAttachmentParseForSKU": {
    color: "yellow",
    text: "Attachment Parsed"
  },
  "ErrorOCRAttachmentParseForSKU": {
    color: "red",
    text: "Attachment Parse Error"
  },
  "InvalidAttachmentForSKU": {
    color: "red",
    text: "Invalid Attachment"
  },
  "SuccessfulAppointmentPODataCreatedForSKU": {
    color: "green",
    text: "PO Created"
  },
  "SuccessSalesforceAppointmentDataUploaded": {
    color: "green",
    text: "Data Saved"
  },
  "ErrorSalesforceAppointmentDataUploaded": {
    color: "red",
    text: "Data Error"
  },
}


export default function POBadge({state}) {

  const { color, text } = STATE_MAPPING[state]

  return (
    <Badge
      color={color}
      text={text}
    />
  )
}