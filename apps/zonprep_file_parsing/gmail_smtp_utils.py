from django.core.mail import EmailMessage
from django.conf import settings

class GmailSMTPUtility():
    def __init__(self):
        self.sender = settings.EMAIL_HOST_USER
        self.reply_to = settings.EMAIL_HOST_USER

    def send_email(self, to=None, subject=None, message_text=None):
        email = EmailMessage(
            subject,
            message_text,
            self.sender,
            [to],
            reply_to=[self.reply_to] # Enforce Reply-To
        )
        email.send()
