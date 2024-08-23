import React from 'react'



export default function SearchAppointmentOrPO({searchTerm, setSearchTerm}) {
  return (
    <div>
      <label htmlFor="search" className="block text-sm font-medium leading-6 text-gray-900">
        Quick search for Appointment ID or PO Number
      </label>
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