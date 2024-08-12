from django.db import models

from apps.utils.models import BaseModel

from .state import CREATED

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