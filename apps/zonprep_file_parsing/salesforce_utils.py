from django.conf import settings

from simple_salesforce import Salesforce

class SalesForceCreateError(Exception):
    """Error creating appointment in Salesforce"""
    pass

class SalesforceUtils:
    def __init__(self):
        self.instance = Salesforce(
            username=settings.SALESFORCE_USERNAME,
            password=settings.SALESFORCE_PASSWORD,
            security_token=settings.SALESFORCE_SECURITY_TOKEN
        )

    # appt will be a ZonprepAppointment object
    # try this and catche it with the SalesForceCreateError
    def create_appointment(self, appt):
        if self.does_appointment_exist(appt):
            result = {
                "success": True,
                "created": False,
                "data":{
                    "message": F"Appointment {appt.p_appointment_id} already exists in salesforce",
                    "sf_appointment_id": None
                } 
            } 
            return result["created"], result["success"], result["data"]

        list_of_records = [
            {
                "Name": appt.p_appointment_id,
                "Actual_Arrival_Date__c": appt.p_appointment_date,
                "Appointment_type__c": appt.p_appointment_type,
                "Carrier__c": appt.p_carrier,
                "Carrier_request_delivery_time_and_date__c": appt.p_carrier_request_delivery_date,
                "Cartons__c": appt.p_cartons,
                "Dock_Door__c": appt.p_dock_door,
                "Freight_terms__c": appt.p_freight_terms,
                "Pallets__c": appt.p_pallets,
                "Priority_score__c": appt.p_percent_needed,
                "Priority_type__c": appt.p_priority_type,
                "Schedule_Date__c": appt.p_appointment_date,
                "Truck_location__c": appt.p_truck_location,
                "Units__c": appt.p_units
            }
        ]
        result = self.instance.bulk.Appointment_ID__c.insert(list_of_records)
        # only one will be created but we're using bulk so get the list.
        created = result[0].get("success", False)
        id = result[0].get("id", None)
        data={
            "message": F"Appointment {appt.p_appointment_id} created with ID {id} in salesforce",
            "sf_appointment_id": id
        }
        success=True
        return created, success, data

    def does_appointment_exist(self, appt):
        soql_query = F"""SELECT
            Name,
            Actual_Arrival_Date__c,
            Appointment_type__c,
            Carrier__c,
            Carrier_request_delivery_time_and_date__c,
            Cartons__c,
            Dock_Door__c,
            Freight_terms__c,
            Pallets__c,
            Priority_score__c,
            Priority_type__c,
            Schedule_Date__c,
            Truck_location__c,
            Units__c
        From Appointment_ID__c
        WHERE Name = '{appt.p_appointment_id}'
        """
        result = self.instance.query(soql_query)
        if result['totalSize'] == 0:
            return False

        return True

    def get_appointment_id(self, appt):
        soql_query = F"""SELECT
            Id,
            Name,
            Actual_Arrival_Date__c,
            Appointment_type__c,
            Carrier__c,
            Carrier_request_delivery_time_and_date__c,
            Cartons__c,
            Dock_Door__c,
            Freight_terms__c,
            Pallets__c,
            Priority_score__c,
            Priority_type__c,
            Schedule_Date__c,
            Truck_location__c,
            Units__c
        From Appointment_ID__c
        WHERE Name = '{appt.p_appointment_id}'
        """
        result = self.instance.query(soql_query)
        if result['totalSize'] == 0:
            return None

        return result['records'][0]['Id']

    # note only do this once you've created the appointment.
    # returns the list of purchase orders if they were created or not.
    def create_purchase_orders(self, appt, sf_appointment_id=None):
        # get the appointment if it doesn't exist
        if sf_appointment_id is None:
            sf_appointment_id = self.get_appointment_id(appt)

        list_of_new_records = []

        list_of_existing = []
        # build the list of records
        for index, po in enumerate(appt.purchase_orders.all()):
            # check if po exists
            does_po_exist = self.does_po_exist(po.p_po_number) # returns the number or non./
            # create the data for the record so that it inserts a value.
            if does_po_exist:
                sf_po_id_number = does_po_exist
                list_of_existing.append({
                    "index_to_insert": index,
                    "data_to_insert":{
                        'success': True,
                        'created': False,
                        'id': sf_po_id_number,
                        'errors': []
                    }
                })
                continue

            # create the record if it's not there.
            cartons = 0
            if po.p_cartons:
                cartons = int(po.p_cartons)
            pallets = 0
            if po.p_pallets:
                pallets = int(po.p_pallets)

            record = {
                'Name': po.p_po_number,
                'Appointment_ID__c': sf_appointment_id,
                'ARN__c': po.p_arn,
                'ASNs__c': po.p_asn,
                'BOLs__c': po.p_bols,
                'Cartons__c': cartons,
                'Freight_terms__c': po.p_freight_terms,
                'Pallets__c': pallets,
                'PRO__c': po.p_pro,
                'Shipment_Label__c': po.p_shipment_label,
                'Vendor__c': po.p_vendor
            }
            list_of_new_records.append(record)
        
        result = self.instance.bulk.POs__c.insert(list_of_new_records)
        
        # insert the existing records into the list.
        if len(list_of_existing) > 0:
            for existing in list_of_existing:
                result.insert(existing['index_to_insert'], existing['data_to_insert'])

        # return the results
        return result

    def does_po_exist(self, po):
        soql_query = F"""SELECT
            Id,
            Name,
            Appointment_ID__c,
            ARN__c,
            ASNs__c,
            BOLs__c,
            Cartons__c,
            Freight_terms__c,
            Pallets__c,
            PRO__c,
            Shipment_Label__c,
            Vendor__c
        From POs__c
        WHERE Name = '{po}'
        """
        result = self.instance.query(soql_query)
        if result['totalSize'] == 0:
            return None

        return result['records'][0]['Id']
        

    