from django.core.management.base import BaseCommand

from apps.zonprep_file_parsing.models import ZonprepAppointment
from apps.zonprep_file_parsing.state import ZonprepAppointmentState, ZonprepPurchaseOrderState

class Command(BaseCommand):
    help = 'Upload Data to Salesforce'

    def handle(self, *args, **kwargs):
        appointments = ZonprepAppointment.objects.filter(
            state=ZonprepAppointmentState.SUCCESSFUL_APPOINTMENT_INFO_UPDATED
        )

        for appt in appointments:
            # create the appoiintment in salesforce
            _, data = appt.create_appointment_in_salesforce()

            # print the message of the appointment if it's created.
            print(data["message"])

            # create the purchase orders in salesforce
            results = appt.create_purchase_orders_in_salesforce(
                sf_appointment_id=data['sf_appointment_id']
            )

            # print the message of the purchase orders.
            for result in results:
                print(result["message"])

