from django.contrib import admin

# Register your models here.

from .models import (ZonprepAppointment, ExternalFulfillmentEmail,
                     ZonprepPurchaseOrder, ZonprepAppointmentTask)

admin.site.register(ZonprepAppointment)
admin.site.register(ExternalFulfillmentEmail)
admin.site.register(ZonprepPurchaseOrder)
admin.site.register(ZonprepAppointmentTask)
