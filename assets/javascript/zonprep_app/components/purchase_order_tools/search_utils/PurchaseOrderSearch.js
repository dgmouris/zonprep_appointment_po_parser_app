import React,{useEffect} from 'react'
import { useSearchParams } from 'react-router-dom';

import { useQueryClient } from '@tanstack/react-query';

export default function PurchaseOrderSearch({searchTerm, setSearchTerm}) {
  const [searchParams, setSearchParams] = useSearchParams();

  const queryClient = useQueryClient();

  useEffect(() => {
    let search = searchParams.get('search')
    if (search && !searchTerm ) {
      setSearchTerm(search)
    }
  }, [searchParams])

  useEffect(() => {
    if (searchTerm) {
      searchParams.set('search', searchTerm);
      setSearchParams(searchParams);
      queryClient.invalidateQueries({ queryKey: ['search_purchase_orders'] })
    }
  }, [searchTerm])

  return (
    <div>
      <div className="">

        <label htmlFor="search" className="flex-grow block text-sm font-medium leading-6 text-gray-900">
          Search for Purchase Orders
        </label>
        <p className="mt-2 text-sm text-gray-700">
          A Search through of all the purchase in your account including their appointment number, purchase order number, scac and vendor.
        </p>
      </div>
      <div className="relative mt-2 flex items-center">
        <input
          id="search"
          name="search"
          type="text"
          className="block w-full rounded-md border-0 py-1.5 px-1 pr-14 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <div className="absolute inset-y-0 right-0 flex py-1.5 pr-1.5">
          <button className="inline-flex items-center rounded border border-gray-200 px-1 font-sans text-xs text-gray-400">
            Search
          </button>
        </div>
      </div>
    </div>
  )
}