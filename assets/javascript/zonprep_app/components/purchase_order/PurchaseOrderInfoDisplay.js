import React from 'react'

const PURCHASE_ORDER_DATA_MAPPING = {
  "created_at": {
    "label": "Created",
    "type": "str"
  },
  "updated_at": {
    "label": "Last Updated",
    "type": "str"
  },
  "p_shipment_id": {
    "label": "Shipment ID",
    "type": "str"
  },
  "p_pallets": {
    "label": "Pallets",
    "type": "str"
  },
  "p_cartons": {
    "label": "Cartons",
    "type": "str"
  },
  "p_units": {
    "label": "Units",
    "type": "str"
  },
  "p_pro": {
    "label": "PRO",
    "type": "str"
  },
  "p_bols": {
    "label": "BOLs",
    "type": "str"
  },
  "p_asn": {
    "label": "ASN",
    "type": "str"
  },
  "p_arn": {
    "label": "ARN",
    "type": "str"
  },
  "p_freight_terms": {
    "label": "Freight Terms",
    "type": "str"
  },
  "p_vendor": {
    "label": "Vendor",
    "type": "str"
  },
  "p_shipment_label": {
    "label": "Shipment Label",
    "type": "str"
  },
  "appointment": {
    "label": "Appointment",
    "type": "str"
  },
}

export default function PurchaseOrderInfoDisplay({data}) {
  return (
    <div>
      <div className="px-4 sm:px-0">
        <h3 className="text-base font-semibold leading-7 text-gray-900">Purchase Order</h3>
        <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">Purchase Order Details</p>
      </div>
      <div className="mt-6 border-t border-gray-100">
        <dl className="divide-y divide-gray-100">
          <div className="px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-0">
            <dt className="text-sm font-medium leading-6 text-gray-900">Purchase Order</dt>
            <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">{data.p_po_number}</dd>
          </div>
          {
            Object.keys(PURCHASE_ORDER_DATA_MAPPING).map((key) => {
              console.log(key)
              console.log(data[key])
              if (data[key]) {
                return (
                  <div key={key} className="px-4 py-6 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-0">
                    <dt className="text-sm font-medium leading-6 text-gray-900">{PURCHASE_ORDER_DATA_MAPPING[key].label}</dt>
                    <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">{data[key]}</dd>
                  </div>
                )
              }
            })
          }
        </dl>
      </div>
    </div>
  )
}
