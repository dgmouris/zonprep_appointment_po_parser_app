import csv

from .models import ZonprepAppointment
from .state import ZonprepAppointmentState

'''
Read the CSV file which should have one column with the appointment id.
Create a ZonprepAppointment object for each row in the CSV file.

csv_file: The CSV file object.
send_to_external_fullfillment: a boolean

'''
def process_csv(csv_file, send_to_external_fullfillment=None):
    # Logic to process the CSV file
    data = csv_file.read().decode('utf-8').splitlines()
    reader = csv.reader(data)
    appointment_results = {
        "created_appointments": 0,
        "already_created_appointments": 0
    }
    appointment_state = ZonprepAppointmentState.CREATED
    if send_to_external_fullfillment:
        # Note: this state is going to be used to send the state to external fulfillment.
        appointment_state = ZonprepAppointmentState.CREATED
    else:
        appointment_state = ZonprepAppointmentState.SENT_TO_FULFILLMENT

    for row in reader:
        appointment_id = row[0]
        _, created = ZonprepAppointment.create_appointment(appointment_id,
                                                           appointment_state=appointment_state)
        if created:
            appointment_results["created_appointments"] += 1
        else:
            appointment_results["already_created_appointments"] += 1
        print(row)  # Process each row

    return appointment_results