
from abc import ABC, abstractmethod
from django.core.files import File
import csv
import tempfile


from .models import ZonprepReports, ZonprepAppointment
from .state import ZonprepAppointmentState

class Report(ABC):
    REPORT_TYPE = None

    def __init__(self):
        self.report_file=None
        self.start = None
        self.end = None

    @staticmethod
    def get_report(report_type):
        if report_type == AveragePalletCountPerScac.REPORT_TYPE:
            return AveragePalletCountPerScac()
        elif report_type == UniqueVendorCodePerApptCount.REPORT_TYPE:
            return UniqueVendorCodePerApptCount()
        return None
    # classes to be implemented
    # you need to set the start, end, and report_file class vars
    @abstractmethod
    def generate_report(self, start, end):
        pass

    def save_report(self):
        with open(self.report_file, 'rb') as temp_file:
            file = File(
                temp_file,
                name=F"{self.REPORT_TYPE}-from_{self.start.date()}_to_{self.end.date()}.csv"
            )
            report = ZonprepReports.objects.create(
                report_type=self.REPORT_TYPE,
                report_document=file,
                report_start_date=self.start.date(),
                report_end_date=self.end.date()
            )
            return report
        return None


class AveragePalletCountPerScac(Report):
    REPORT_TYPE = 'average_pallet_count_per_scac'

    def generate_report(self, start, end):
        self.start = start
        self.end = end

        appts =ZonprepAppointment.objects.filter(
            state=ZonprepAppointmentState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
        ).exclude(
            p_pallets__in=["", "0"],
            p_scac__isnull=True,
            p_scac="",
            created_at__range=[start, end]
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

        report_csv_rows = [["scac", "average_pallets", "pallet_count", "appointments"]]
        for scac, values, in average_pallet_count_per_scac.items():
            report_csv_rows.append([
                scac,
                values["average"],
                values["pallets"],
                values["appointments"]
            ])

        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.csv') as temp_file:
            writer = csv.writer(temp_file)
            # # Write the rows
            writer.writerows(report_csv_rows)
            #
            temp_file.flush()
            #
            self.report_file = temp_file.name
            # Return the path to the temporary file
            return temp_file

        return None

class UniqueVendorCodePerApptCount(Report):
    REPORT_TYPE = 'unique_vendor_code_per_appointment_count'

    def generate_report(self, start, end):
        self.start = start
        self.end = end

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
            state=ZonprepAppointmentState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED,
            created_at__range=[start, end]
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

        with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.csv') as temp_file:
            writer = csv.writer(temp_file)
            # # Write the rows
            writer.writerows(report_csv_rows)
            #
            temp_file.flush()
            #
            self.report_file = temp_file.name
            # Return the path to the temporary file
            return temp_file

        return None