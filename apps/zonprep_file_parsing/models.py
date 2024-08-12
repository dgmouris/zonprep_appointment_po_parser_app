from django.db import models



class ZonprepAppointment(models.Model):
    # appointment id given by the zonprep
    appointment_id = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.appointment_id} - {self.state}"
