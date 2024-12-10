from django.contrib import admin

# Register your models here.

from .models import (ZonprepAppointment, ExternalFulfillmentEmail,
                     ZonprepPurchaseOrder, ZonprepAppointmentTask,
                     GmailTokenCredentials, ZonprepPOImageAttachments,
                     ZonprepPurchaseOrderSKU, ZonprepReports,
                     TypeCEmailDetails)

admin.site.register(ZonprepAppointmentTask)
admin.site.register(ExternalFulfillmentEmail)
admin.site.register(GmailTokenCredentials)
admin.site.register(ZonprepAppointment)
admin.site.register(ZonprepPurchaseOrder)
admin.site.register(ZonprepPOImageAttachments)
admin.site.register(ZonprepPurchaseOrderSKU)
admin.site.register(ZonprepReports)
admin.site.register(TypeCEmailDetails)
