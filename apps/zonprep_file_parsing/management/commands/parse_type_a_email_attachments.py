from django.core.management.base import BaseCommand
from apps.zonprep_file_parsing.models import ZonprepAppointment


class Command(BaseCommand):
    help = 'Parses Emails recieved from External Fulfillment and updates the zonprep for appointments'

    def handle(self, *args, **kwargs):
        self.stdout.write("Parsing Emails recieved from External Fulfillment for appointments...")

        ZonprepAppointment.parse_type_a_appointments_from_emails()

        self.stdout.write("Complete!")
