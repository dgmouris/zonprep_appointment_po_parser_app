from django.db import models
from django.core.exceptions import ValidationError

from apps.utils.models import BaseModel

from .state import CREATED, SENT_TO_FULFILLMENT
from .gmail_utils import GmailUtility


class ZonprepAppointment(BaseModel):
    # appointment id given by the zonprep
    appointment_id = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.appointment_id} - {self.state}"


    @staticmethod
    def create_appointment(appointment_id):
        return ZonprepAppointment.objects.get_or_create(
            appointment_id=appointment_id,
            state=CREATED
        )


    def get_email_subject(self):
        return F"POD for freight: {self.appointment_id}"

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


    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)

        # Move the state to SENT_TO_FULFILLMENT and send the email.
        if self.state == CREATED:
            message = self.send_external_appointment_request_email()
            if message:
                self.state = SENT_TO_FULFILLMENT
                self.save()

'''
This singleton model is solely for the purpose of storing
- external fulfillment email
'''
class SingletonModel(models.Model):
    # Define your fields here

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