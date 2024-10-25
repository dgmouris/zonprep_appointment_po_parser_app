from django.core.management.base import BaseCommand
from apps.zonprep_file_parsing.models import ZonprepPurchaseOrder


class Command(BaseCommand):
    help = 'Sends out purchase orders emails to external fulfillment.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Sending out purchase orders emails to external fulfillment...")

        ZonprepPurchaseOrder.move_state_to_sent_to_fulfillment()

        self.stdout.write("Complete!")
