import React from 'react'


const stats = [
  { name: 'Successfully %', stat: '98.16%' },
  { name: 'Successfully #', stat: '85' },
  { name: 'No Response #', stat: '2' },
]

export default function AppointmentParsedDataDisplay({data}) {
  return (
    <div className="pt-4">
      <h3 className="text-base font-semibold leading-6 text-gray-900">Stats for Today</h3>
      <dl className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-3">
        {stats.map((item) => (
          <div key={item.name} className="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
            <dt className="truncate text-sm font-medium text-gray-500">{item.name}</dt>
            <dd className="mt-1 text-3xl font-semibold tracking-tight text-gray-900">{item.stat}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}