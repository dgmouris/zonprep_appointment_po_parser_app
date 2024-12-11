import React, {useState, useEffect} from 'react'

import { Link } from 'react-router-dom'

import { useQueryClient, useMutation } from '@tanstack/react-query';
import { getCSRFToken } from '@/components//utils/csrf';

import { Checkbox } from '@/components/utils/uikit/checkbox'
import POBadge from './POBadge'

import { useNotification } from '@/components/utils/notifications/AppNotification';

export default function SearchResultsTable({rows, searchTerm, isPending}) {
  if (!rows) {
    rows = []
  }
  const [data, setData] = useState([])
  const [selectAll , setSelectAll] = useState(false)
  const [requestPOData, setRequestPOData] = useState({})

  const showNotification = useNotification();

  // initialize queryClient
  const queryClient = useQueryClient();

  // map the rows to add a checked property
  useEffect(() => {
    if (isPending) {
      return
    }
    if (!searchTerm) {
      return
    }
    const mappedRows = rows.map(row => {
      return {
        checked: false,
        ...row
      }
    })
    setData(mappedRows)
  }, [rows])

  const onChangeSelectOrDeselectAll = () => {
    setSelectAll(!selectAll)
    const updatedData = data.map(row => {
      return {
        ...row,
        checked: !selectAll
      }
    })
    setData(updatedData)
  }

  const countSelected = () => {
    return data.filter(row => row.checked).length
  }

  const onChangeSelectOrDeselect = (row) => {
    const updatedData = data.map(dataRow => {

      if (dataRow.id === row.id) {
        return {
          ...dataRow,
          checked: !dataRow.checked
        }
      }
      return dataRow
    })
    setData(updatedData)
  }


  const poFromSelectedMutation = useMutation({
    mutationFn: () => {
      return fetch(`/app/v1/actions/set_purchase_orders_to_be_sent/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify(requestPOData)
      })
    },
    onSuccess: (responseData) => {
      console.log(responseData)
      if (responseData.status === 200) {
        showNotification({
          title: 'Requesting POs from fulfillment',
          description: 'Waiting for a response',
          type: 'success'
        })
      } else {
        showNotification({
          title: 'Error requesting POs from fulfillment',
          description: 'There was an error requesting the POs',
          type: 'error'
        })
      }
      queryClient.invalidateQueries({ queryKey: ['search_purchase_orders'] })
    },
    onError: (error) => {
      showNotification({
        title: 'Error requesting POs from fulfillment',
        description: 'There was an error requesting the POs',
        type: 'error'
      })
      queryClient.invalidateQueries({ queryKey: ['search_purchase_orders'] })
    },
   })



  const requestPOFromSelected = async () => {
    const po_ids = data.filter(row => row.checked).map(row => row.id)
    setRequestPOData({
      list_of_po_ids: po_ids,
    })
    poFromSelectedMutation.mutate();
  }

  const requestPOFromSearch = async () => {
    setRequestPOData({
      search_term: searchTerm,
    })
    poFromSelectedMutation.mutate();
  }

  if (!searchTerm) {
    return <div>Enter a search</div>
  }

  if (isPending) {
    return <div>Loading...</div>
  }


  return (
    <div className="mt-4">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-base font-semibold text-gray-900">Purchase Orders ({data.length})</h1>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none flex">
          <button
            type="button"
            className="rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
            onClick={onChangeSelectOrDeselectAll}
          >
            {selectAll ? "Deselect All" : "Select All"}
          </button>
          <button
            type="button"
            className="ml-2 bb-1 inline-flex items-center gap-x-1.5 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            onClick={requestPOFromSelected}
            >
            Request PO for Selected ({countSelected()})
          </button>
          <button
            type="button"
            className="ml-2 bb-1 inline-flex items-center gap-x-1.5 rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            onClick={requestPOFromSearch}
          >
            Request PO for all in ({searchTerm})
          </button>
        </div>
      </div>

      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <table className="min-w-full divide-y divide-gray-300">
              <thead>
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0">
                    <Checkbox
                      checked={selectAll}
                      onChange={onChangeSelectOrDeselectAll}
                    />
                  </th>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0">
                    Purchase Order Number
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Appointment Number
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    SCAC
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    Vendor
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 text-right ">
                    State
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {data.map((row) => (
                  <tr key={row.id}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-0">
                      <Checkbox
                        checked={row.checked}
                        onChange={() => onChangeSelectOrDeselect(row)}
                      />
                    </td>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-indigo-600 hover:text-indigo-900 sm:pl-0">
                      <Link to={`/purchase_order/${row.p_po_number}`}>
                        {row.p_po_number}
                      </Link>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-indigo-600 hover:text-indigo-900">
                      <Link to={`/appointment/${row.appointment.p_appointment_id}`}>
                        {row.appointment.p_appointment_id}
                      </Link>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{row.appointment.p_scac}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{row.p_vendor}</td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                      <POBadge state={row.state} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
