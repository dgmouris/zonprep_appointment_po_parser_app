import React from 'react'

import SearchResults from '../home/search_utils/SearchResults'

export default function RelatedPurchaseOrdersList({purchaseOrders}) {
  if (purchaseOrders.length === 0) {
    return (
      <section className="app-card">
        <h3 className="text-base font-semibold leading-7 text-gray-900">Purchase Orders</h3>
        <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">No Purchase orders linked to this appointment</p>
      </section>
    )
  }
  
  return (
    <section className="app-card">
              <h3 className="text-base font-semibold leading-7 text-gray-900">Purchase Orders</h3>
              <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">All Purchase orders linked to this appointment</p>
      <SearchResults data={purchaseOrders} loading={false}/>
    </section>
  )
}