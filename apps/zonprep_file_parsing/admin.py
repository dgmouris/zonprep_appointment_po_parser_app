from django.contrib import admin

# Register your models here.

from .models import (ZonprepAppointment, ExternalFulfillmentEmail,
                     ZonprepPurchaseOrder, ZonprepAppointmentTask,
                     GmailTokenCredentials, ZonprepPOImageAttachments)

admin.site.register(ZonprepAppointment)
admin.site.register(ExternalFulfillmentEmail)
admin.site.register(ZonprepPurchaseOrder)
admin.site.register(ZonprepPOImageAttachments)
admin.site.register(ZonprepAppointmentTask)
admin.site.register(GmailTokenCredentials)
