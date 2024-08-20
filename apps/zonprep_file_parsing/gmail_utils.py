from django.conf import settings

import base64
from typing import List
import time
import os
# from google_apis import create_service
import datetime
from collections import namedtuple
from google_auth_oauthlib.flow import InstalledAppFlow

import json
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt

class GmailConnectionError(Exception): 
    """Error connecting to Gmail API."""

class GmailSendingError(Exception):
    """Error sending email through Gmail API."""

class GmailException(Exception):
    """Gmail base exception class"""
    pass

class NoEmailsFound(GmailException):
    """No emails are found"""
    pass


class GmailUtility:
    def __init__(self, user_id=None):
        
        api_name = 'gmail'
        api_version = 'v1'
        scopes = ['https://mail.google.com/']
        service_data = {
            "api_name": api_name,
            "api_version": api_version,
            "scopes": scopes,
        }
        
        # this needs to be set in the .env file
        service_data['client_secret_json'] = settings.GMAIL_SECRET_CREDENTIALS
        
        self.service = self.create_service(
            **service_data
        )
        # set the user_id to the creds instance created above.
        if not user_id:
            user_id = self.gmail_token_creds.gmail_user_id
        self.user_id = user_id

    def _get_creds_instance(self):
        from .models import GmailTokenCredentials
        creds = GmailTokenCredentials.load()
        self.gmail_token_creds = creds
        return creds

    # connect to gmail and create the service so that you can make api calls.
    def create_service(
            self,
            client_secret_file=None,
            client_secret_json=None,
            api_name=None,
            api_version=None,
            scopes=None,
            prefix=''
        ):

        gmail_token_creds = self._get_creds_instance()
        
        # client_secret = json.loads(CLIENT_SECRET_JSON)
        client_secret = gmail_token_creds.secret_credentials

        API_SERVICE_NAME = api_name
        API_VERSION = api_version
        SCOPES = [scope for scope in scopes]
        
        creds = None
        working_dir = os.getcwd()
        token_dir = 'gmail_token_files'
        token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'

        # handle the null case for tokens.
        creds = None
        if gmail_token_creds.token is not None:
        # get the credentails from the token in the database.
            creds = Credentials.from_authorized_user_info(gmail_token_creds.token, scopes=SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = None
                flow = InstalledAppFlow.from_client_config(client_secret, SCOPES)
                creds = flow.run_local_server(port=0)

            # write to database.
            creds_dict = json.loads(creds.to_json())
            gmail_token_creds.update_token(creds_dict)

            with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
                token.write(creds.to_json())

        try:
            service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
            # This should be logged instead of printed
            # print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
            return service
        except Exception as e:
            print(e)
            print(f'Failed to create service instance for {API_SERVICE_NAME}')
            # os.remove(os.path.join(working_dir, token_dir, token_file))
            return None

    def search_emails(self, query_string: str, label_ids: List):
        try:
            message_list_response = self.service.users().messages().list(
                userId=self.user_id,
                q=query_string,
                labelIds=label_ids
            ).execute()

            message_items = message_list_response.get('messages', [])
            next_page_token = message_list_response.get('nextPageToken', None)

            while next_page_token:
                time.sleep(1)
                message_list_response = self.service.users().messages().list(
                    userId=self.user_id,
                    q=query_string,
                    labelIds=label_ids,
                    pageToken=next_page_token
                ).execute()

                message_items.extend(message_list_response.get('messages', []))
                next_page_token = message_list_response.get('nextPageToken', None)


            return message_items
        except Exception as e:
            raise NoEmailsFound(f'No emails found with the query: {query_string}')

    def get_file_data(self, message_id, attachment_id, file_name, save_location):
        response = self.service.users().messages().attachments().get(
            userId=self.user_id,
            messageId=message_id,
            id=attachment_id
        ).execute()

        file_data = base64.urlsafe_b64decode(response['data'].encode('UTF-8'))
        return file_data


    def get_message_detail(self, message_id, msg_format='metadata', metadata_headers=None):
        message_detail = self.service.users().messages().get(
            userId=self.user_id,
            id=message_id,
            format=msg_format,
            metadataHeaders=metadata_headers
        ).execute()
        return message_detail


    # send message
    def create_message(sender, to, subject, message_text):
        """Create a message for an email."""
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}

    def send_email(self, sender=None, to=None, subject=None, message_text=None):
        """Create a message for an email."""
        if sender is None:
            sender = self.gmail_token_creds.gmail_user_id
        
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message = {'raw': raw_message}
        """Send an email message."""
        
        try:
            message = self.service.users().messages().send(
                userId=self.user_id,
                body=message
            ).execute()
            print(f'Message Id: {message["id"]}')
            return message
        except HttpError as error:
            raise GmailSendingError(f'An error occurred: {error}')

    def get_message_attachment(self, email=None, message_detail=None):
        if email is None:
            return
        if message_detail is None:
            message_detail = self.get_message_detail(email['id'], msg_format='full')
        message_detail_payload = message_detail['payload']
        if 'parts' in message_detail_payload:
            for msg_payload in message_detail_payload['parts']:
                if msg_payload['filename']:
                    attachment_id = None
                    if 'attachmentId' in msg_payload['body']:
                        attachment_id = msg_payload['body']['attachmentId']
                    file_name = msg_payload['filename']
                    save_location = os.path.join(os.getcwd(), 'attachments', file_name)
                    file_data = self.get_file_data(email['id'], attachment_id, file_name, save_location)
        
        return file_data