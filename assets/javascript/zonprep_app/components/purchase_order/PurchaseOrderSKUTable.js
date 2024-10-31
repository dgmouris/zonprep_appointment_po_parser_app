import React from 'react'

const people = [
  { name: 'Lindsay Walton', title: 'Front-end Developer', email: 'lindsay.walton@example.com', role: 'Member' },
  // More people...
]

export default function PurchaseOrderSKUTable({skus}) {
  console.log(skus)
  if (skus.length === 0) {
    return <section className="app-card">
    <div className="">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-base font-semibold text-gray-900">No Type C Data associated to this purchase order</h1>
        </div>
      </div>
      </div>
    </section>
  }
  return (
    <section className="app-card">
      <div className="">
        <div className="sm:flex sm:items-center">
          <div className="sm:flex-auto">
            <h1 className="text-base font-semibold text-gray-900">Type C Data associated to purchase order</h1>
            <p className="mt-2 text-sm text-gray-700">
              A list of data associated to this purchase order
            </p>
          </div>
        </div>
        <div className="mt-8 flow-root">
          <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                        fnsku
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        iaid
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        msku
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        shipped quantity
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        weight
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        created date
                      </th>
                      <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                        updated date
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {skus.map((sku) => (
                      <tr key={sku.id}>
                        <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                          {sku.p_fnsku}
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{sku.p_iaid}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{sku.p_msku}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{sku.p_shipped_quantity}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{sku.p_weight}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{sku.p_create_date}</td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{sku.p_update_date}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
