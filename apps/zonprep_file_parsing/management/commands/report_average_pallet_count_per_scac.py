import csv
from django.core.management.base import BaseCommand

from apps.zonprep_file_parsing.models import ZonprepAppointment
from apps.zonprep_file_parsing.state import ZonprepAppointmentState, ZonprepPurchaseOrderState

class Command(BaseCommand):
    help = '''
        Average pallet count per scac
    '''

    def handle(self, *args, **kwargs):
        appts =ZonprepAppointment.objects.filter(
            state=ZonprepAppointmentState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
        ).exclude(
            p_pallets__in=["", "0"],
            p_scac__isnull=True,
            p_scac=""
        ).prefetch_related("purchase_orders")

        average_pallet_count_per_scac = {}
        for appt in appts:
            # remove the older values of p_scac
            if appt.p_scac is None:
                continue
            # remove the values of pallets that are zero
            pallets = int(appt.p_pallets)
            if pallets == 0:
                continue

            if appt.p_scac not in average_pallet_count_per_scac.keys():
                average_pallet_count_per_scac[appt.p_scac] = {
                    "pallets": pallets,
                    "appointments": 1,
                    "average": pallets
                }
            else:
                average_pallet_count_per_scac[appt.p_scac]["pallets"] = (
                    average_pallet_count_per_scac[appt.p_scac]["pallets"]
                    + pallets)
                average_pallet_count_per_scac[appt.p_scac]["appointments"] = (
                    average_pallet_count_per_scac[appt.p_scac]["appointments"]
                    +1
                )
                average_pallet_count_per_scac[appt.p_scac]["average"] = (
                    average_pallet_count_per_scac[appt.p_scac]["pallets"]
                    / average_pallet_count_per_scac[appt.p_scac]["appointments"]
                )

        report_csv_rows = [["scac", "average_pallets", "appointments", "count"]]
        for scac, values, in average_pallet_count_per_scac.items():
            report_csv_rows.append([
                scac,
                values["average"],
                values["pallets"],
                values["appointments"]
            ])

        report_name = 'random_reports/average_pallet_count_per_scac.csv'
        with open(report_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            # # Write the rows
            writer.writerows(report_csv_rows)

        print(F"Completed report {report_name}")



