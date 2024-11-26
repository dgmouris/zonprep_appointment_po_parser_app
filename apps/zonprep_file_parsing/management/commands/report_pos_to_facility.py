import csv
from django.core.management.base import BaseCommand
from apps.zonprep_file_parsing.models import ZonprepPurchaseOrder
from apps.zonprep_file_parsing.state import ZonprepAppointmentState, ZonprepPurchaseOrderState
from apps.zonprep_file_parsing.models import ZonprepAppointment

class Command(BaseCommand):
    help = '''
        Average pallet count per scac
    '''

    def handle(self, *args, **kwargs):
        appts = ZonprepAppointment.objects.filter(
            state=ZonprepAppointmentState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
        ).prefetch_related("purchase_orders")

        facilty_po_count_mapping = {}

        for appt in appts:
            count_of_po = len(appt.purchase_orders.all())
            if appt.fc_code is None:
                continue
            if appt.fc_code not in facilty_po_count_mapping.keys():
                facilty_po_count_mapping[appt.fc_code] = {
                    "po_count": count_of_po,
                    "appt_count": 1,
                    "average": count_of_po
                }
            else:
                facilty_po_count_mapping[appt.fc_code]["po_count"] = (
                    facilty_po_count_mapping[appt.fc_code]["po_count"]
                    + count_of_po)
                facilty_po_count_mapping[appt.fc_code]["appt_count"] = (
                    facilty_po_count_mapping[appt.fc_code]["appt_count"]
                    + 1
                )
                facilty_po_count_mapping[appt.fc_code]["average"] = (
                    facilty_po_count_mapping[appt.fc_code]["po_count"]
                    / facilty_po_count_mapping[appt.fc_code]["appt_count"]
                )

        report_csv_rows = [["facility_code", "average_po_count", "po_count", "appt_count"]]
        for fc_code, values, in facilty_po_count_mapping.items():
            report_csv_rows.append([
                fc_code,
                values["average"],
                values["po_count"],
                values["appt_count"]
            ])

        report_name = 'random_reports/average_po_count_per_facility.csv'
        with open(report_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(report_csv_rows)

        print(F"Completed report {report_name}")

