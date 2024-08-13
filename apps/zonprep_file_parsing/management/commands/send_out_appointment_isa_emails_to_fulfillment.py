from django.core.management.base import BaseCommand
from apps.zonprep_file_parsing.models import ZonprepAppointment


class Command(BaseCommand):
    help = 'Sends out appointment ISA emails to external fulfillment.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Sending out appointment ISA emails to external fulfillment...")

        ZonprepAppointment.move_state_to_sent_to_fulfillment()
        
        self.stdout.write("Complete!")
