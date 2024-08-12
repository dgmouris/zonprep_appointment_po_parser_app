from django.contrib import admin

# Register your models here.

from .models import ZonprepAppointment, ExternalFulfillmentEmail

admin.site.register(ZonprepAppointment)
admin.site.register(ExternalFulfillmentEmail)
