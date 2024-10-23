import csv
from django.core.management.base import BaseCommand

from apps.zonprep_file_parsing.models import ZonprepAppointment
from apps.zonprep_file_parsing.state import ZonprepAppointmentState, ZonprepPurchaseOrderState

class Command(BaseCommand):
    help = '''
        vendor code, count of unique appointments containing that vendor code

    '''

    def handle(self, *args, **kwargs):
        vendor_scac = [
            "FDCC",
            "FDEG",
            "FDEN",
            "FEXF",
            "FLJF",
            "FXFE",
            "FXFW",
            "FXNL",
            "UPSN",
            "UPSS",
            "UPSC",
            "UPSZ",
        ]
        appts =ZonprepAppointment.objects.filter(
            p_scac__in=vendor_scac,
            state=ZonprepAppointmentState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
        ).prefetch_related("purchase_orders")

        all_vendor_codes = {}

        for appt in appts:
            if appt.p_scac not in all_vendor_codes.keys():
                all_vendor_codes[appt.p_scac] = {}
            # set of vendor codes.
            appt_vendor_codes = set([])
            for po in appt.purchase_orders.all():
                po_vendor_codes = po.p_vendor.split(", ")
                appt_vendor_codes.update(po_vendor_codes)
            # deal with all vendor codes:
            for vendor_code in list(appt_vendor_codes):
                if vendor_code == "":
                    continue
                # if it's not in the vendor codes add it in keys.
                if not vendor_code in all_vendor_codes[appt.p_scac].keys():
                    # start the vendor codes
                    all_vendor_codes[appt.p_scac][vendor_code] = 1
                else:
                    all_vendor_codes[appt.p_scac][vendor_code] = all_vendor_codes[appt.p_scac][vendor_code] + 1

        # remove all of the empty scac codes
        all_vendor_codes = {k: v for k, v in all_vendor_codes.items() if v != {}}

        report_csv_rows = [["scac", "vendor", "count"]]
        # format all rows for report
        for scac, vendor_for_scac in all_vendor_codes.items():
            # scac = key
            for vendor, count in vendor_for_scac.items():
                report_csv_rows.append([scac, vendor, count])
        report_name = 'random_reports/unique_vendor_code_per_appointment_count.csv'
        with open(report_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            # # Write the rows
            writer.writerows(report_csv_rows)

        print(F"Completed report {report_name}")
        # print(all_vendor_codes)


'''
Note: wanted ups and

"FDCC"	FedEx Custom Critical
"FDEG"	FEDEX GROUND
"FDEN"	FEDEX (AIR)
"FEXF"	FedEx Freight
"FLJF"	FLT LOGISTICS LLC
"FXFE"	FedEx LTL Freight East
"FXFW"	FedEx LTL Freight West (formerly VIKN – Viking)
"FXNL"	FedEx Freight National (formerly Watkins)
"UPSN"	United Parcel Service
"UPSS"	United Parcel Service
"UPSC"	United Parcel Service
"UPSZ"	United Parcel Service
'''