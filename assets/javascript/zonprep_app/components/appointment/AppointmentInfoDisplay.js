import React from 'react'

const APPOINTMENT_DATA_MAPPING = {
  "p_appointment_id": {
    "label": "Appointment ID",
    "type": "str"
  },
  "state": {
    "label": "state",
    "type": "str"
  },
  "p_appointment_date": {
    "label": "Appointment Date",
    "type": "str"
  },
  "p_appointment_type": {
    "label": "Appointment Type",
    "type": "str"
  },
  "p_carrier": {
    "label": "Carrier",
    "type": "str"
  },
  "p_carrier_request_delivery_date": {
    "label": "Carrier Request Delivery Date",
    "type": "str"
  },
  "p_cartons": {
    "label": "Cartons",
    "type": "str"
  },
  "p_dock_door": {
    "label": "Dock Door",
    "type": "str"
  },
  "p_freight_terms": {
    "label": "Freight Terms",
    "type": "str"
  },
  "p_pallets": {
    "label": "Pallets",
    "type": "str"
  },
  "p_percent_needed": {
    "label": "Percent Needed",
    "type": "str"
  },
  "p_priority_type": {
    "label": "Priority Type",
    "type": "str"
  },
  "p_trailer_number": {
    "label": "Trailer Number",
    "type": "str"
  },
  "p_truck_location": {
    "label": "Truck Location",
    "type": "str"
  },
  "p_units": {
    "label": "Units",
    "type": "str"
  },
  "created_at": {
    "label": "Created",
    "type": "str"
  },
  "updated_at": {
    "label": "Last Updated",
    "type": "str"
  },
}


export default function AppointmentInfoDisplay({data}) {
  return (
    <section className="app-card">
      <div className="px-4 sm:px-0">
        <h3 className="text-base font-semibold leading-7 text-gray-900">Appointment</h3>
        <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">Appointment Details</p>
      </div>
      <div className="mt-6 border-t border-gray-100">
        <dl className="divide-y divide-gray-100">
          <div className="px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-0">
            <dt className="text-sm font-medium leading-6 text-gray-900">Request ID <br/>(From CSV upload)</dt>
            <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">{data.request_id}</dd>
          </div>
          {
            Object.keys(APPOINTMENT_DATA_MAPPING).map((key) => {
              console.log(key)
              console.log(data[key])
              if (data[key]) {
                return (
                  <div key={key} className="px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-0">
                    <dt className="text-sm font-medium leading-6 text-gray-900">{APPOINTMENT_DATA_MAPPING[key].label}</dt>
                    <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">{data[key]}</dd>
                  </div>
                )
              }
            })
          }
        </dl>
      </div>
    </section>
  )
}
