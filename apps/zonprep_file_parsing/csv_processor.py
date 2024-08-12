import csv

from .models import ZonprepAppointment

'''
Read the CSV file which should have one column with the appointment id.
Create a ZonprepAppointment object for each row in the CSV file.

'''
def process_csv(csv_file):
    # Logic to process the CSV file
    data = csv_file.read().decode('utf-8').splitlines()
    reader = csv.reader(data)
    appointment_results = {
        "created_appointments": 0,
        "already_created_appointments": 0
    }
    for row in reader:
        appointment_id = row[0]
        _, created = ZonprepAppointment.create_appointment(appointment_id)
        if created:
            appointment_results["created_appointments"] += 1
        else:
            appointment_results["already_created_appointments"] += 1
        print(row)  # Process each row

    return appointment_results