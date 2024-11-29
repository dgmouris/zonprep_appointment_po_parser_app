from .gmail_utils import GmailUtility
from .gmail_smtp_utils import GmailSMTPUtility
from .sendgrid_utils import SendGridUtility


# this essentially is a utility class that will try to send an email
# through the gmail api, then through the gmail smtp server, and then
# through sendgrid. If all three fail, then it will raise an exception
# this is for greater throughput.
class MassMailerUtility():

    def __init__(self, external_fulfillment=None):
        self.external_fulfillment = external_fulfillment
        self.gmail_utils = GmailUtility()
        self.gmail_smtp_utils = GmailSMTPUtility()
        self.sendgrid_utils = SendGridUtility()


    def send_email(self, to=None, subject=None, message_text=None):
        # Send email
        errors = []

        # Step 1: Try sending with the gmail api from the pod@freight-corp.com account
        try:
            print("Step 1: Trying to send with gmail api")
            message = self.gmail_utils.send_email(
                to=self.xternal_fulfillment.email,
                subject=subject,
                message_text=subject
            )
            print("Sent with gmail api")
            return message
        except Exception as e:
            print("Unsuccessful with gmail api, trying next step")
            errors.append(e)

        # Step 2: Try sending with the gmail smtp server from pod-no-reply@freight-corp.com account
        try:
            print("Step 2: Trying to send with gmail smtp")
            self.gmail_smtp_utils.send_email(
                to=self.external_fulfillment.email,
                subject=subject,
                message_text=subject
            )
            print("Sent with gmail smtp")
            return True
        except Exception as e:
            print("Unsuccessful with gmail smtp, trying next step")
            errors.append(e)

        # Step 3: Try Sending with Sengrid Working.
        # sent through pod@freight-corp.com
        try:
            print("Step 3: Trying to send with sendgrid")
            message = self.sendgrid_utils.send_email(
                sender="pod@freight-corp.com",
                to=self.external_fulfillment.email,
                subject=subject,
                message_text=subject
            )
            print("Sent with sendgrid")
            return message
        except Exception as e:
            print("Unsuccessful with sendgrid, Failed all steps")
            errors.append(e)

        # there was an error in sending the email and it should
        # be raised here, if it hasn't hit on the three steps here
        # then you're hooped.
        raise Exception("\n\n".join(errors))

