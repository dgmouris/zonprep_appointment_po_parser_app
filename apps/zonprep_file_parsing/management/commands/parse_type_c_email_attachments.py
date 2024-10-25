from django.core.management.base import BaseCommand
from apps.zonprep_file_parsing.models import ZonprepPurchaseOrder


class Command(BaseCommand):
    help = 'Parses Emails recieved from External Fulfillment and updates the zonprep for purchase orders'

    def handle(self, *args, **kwargs):
        self.stdout.write("Parsing Emails recieved from External Fulfillment for purchase orders...")

        ZonprepPurchaseOrder.parse_type_c_purchase_orders_from_emails()

        self.stdout.write("Complete!")
