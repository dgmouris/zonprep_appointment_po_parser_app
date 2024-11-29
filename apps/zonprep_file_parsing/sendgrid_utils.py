from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGridUtility:
    def __init__(self):
        self.sendgrid = SendGridAPIClient(
            api_key=settings.SENDGRID_API_KEY
        )

    def send_email(self, sender=None, to=None, subject=None, message_text=None):
        message = Mail(
            from_email=sender,
            to_emails=to,
            subject=subject,
            html_content=message_text
        )
        try:
            response = self.sendgrid.send(message)
            return True
        except Exception as e:
            raise

