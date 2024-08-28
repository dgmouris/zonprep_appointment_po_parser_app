import React from 'react'

import { ChevronRightIcon } from '@heroicons/react/20/solid'

import { useNavigate } from 'react-router-dom'

export default function SearchResults({data, loading, searchTerm}) {
  const navigate = useNavigate()
  
  if (!data) {
    data= []
  }

  const goToAppointmentOrPO = (value, value_type) => {
    if (value_type === 'appointment') {
      navigate(`/appointment/${value}`)
    } else if (value_type === 'request_id') {
      navigate(`/appointment/${value}`)
    } else if (value_type === 'purchase_order') {
      navigate(`/purchase_order/${value}`)
    }
  } 

  const isStartingSearch = () => {
    return data.length === 0 && searchTerm.length === 0
  }
  
  const isNoSearchResults = () => {
    return data.length === 0 && searchTerm.length > 0
  }

  return (
    <ul role="list" className="divide-y divide-gray-100">
      {isStartingSearch() &&
        <li className="py-5 text-center">
          Start By searching for an Appointment ID or PO Number
        </li>
      }
      
      
      {isNoSearchResults()  && <li className="py-5 text-center">No results found</li>}
      
      {data.map((searchResult)=> {
        return <li
          key={searchResult.value}
          className="cursor-pointer relative flex justify-between gap-x-6 py-5"
          onClick={(e) => goToAppointmentOrPO(searchResult.value, searchResult.value_type)}
        >
         <div className="flex min-w-0 gap-x-4">
           <div className="min-w-0 flex-auto">
             <p className="m-0 text-sm font-semibold leading-6 text-gray-900">
               
                <span className="absolute inset-x-0 -top-px bottom-0" />
                {searchResult.value}
              
             </p>
             <p className="mt-1 flex text-xs leading-5 text-gray-500">
               <span className="relative truncate hover:underline">
                { searchResult.value_type === 'appointment' && 'Appointment'}
                { searchResult.value_type === 'purchase_order' && 'Purchase Order'}
                { searchResult.value_type === 'request_id' && 'Request ID'}
                
               </span>
             </p>
           </div>
         </div>
         <div className="flex shrink-0 items-center gap-x-4">
           <div className="hidden sm:flex sm:flex-col sm:items-end">
             {/* 
            Build out the state here for the search result
            Take a look here https://tailwindui.com/components/application-ui/lists/stacked-lists

             */}
           </div>
           <ChevronRightIcon aria-hidden="true" className="h-5 w-5 flex-none text-gray-400" />
         </div>
      </li>
      })}
    </ul>
  )
}