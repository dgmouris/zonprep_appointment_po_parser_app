import React, {useState, useCallback } from 'react'

import PurchaseOrderSearch from './search_utils/PurchaseOrderSearch'
import SearchResultsTable from './search_utils/SearchResultsTable'

import {
  useQuery,
} from '@tanstack/react-query'

export default function PurchaseOrderToolsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  // debounce the searchTerm

  // search function to fetch the values, needs to be longer than 3 characters
  const fetchPurchaseOrders = useCallback(async () => {
    return fetch(`/app/v1/search/by_purchase_order/?q=${searchTerm}`).then((res) =>
      res.json(),
    )
  }, [searchTerm])

  const { isPending, error, data } = useQuery({
    queryKey: ['search_purchase_orders'],
    queryFn: fetchPurchaseOrders,
    enabled: !!searchTerm && searchTerm.length > 3
  })

  if (error) {
    return <div>Error: {error.message}</div>
  }

  return <div>
    <div className="flex flex-col md:flex-row  md:gap-4">
      <div className="w-full md">
        <section className="app-card">
          <div className="px-4 sm:px-0 ">
            <h3 className="text-base font-semibold leading-7 text-gray-900">Purchase Order Tools</h3>
            <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">
              Search by Purchase Order Number, Vendor, Appointment, or SCAC.
            </p>
          </div>
          <div className="mt-5 px-4 sm:px-0">
            <PurchaseOrderSearch
              searchTerm={searchTerm}
              setSearchTerm={setSearchTerm}
            />
            <SearchResultsTable
              rows={data}
              searchTerm={searchTerm}
              isPending={isPending}
            />
          </div>
        </section>
      </div>
    </div>
  </div>

}