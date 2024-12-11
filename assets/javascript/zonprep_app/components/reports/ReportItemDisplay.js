import React from 'react'

import {
  useQuery,
  useQueryClient,
  useMutation
} from '@tanstack/react-query'
import { getCSRFToken } from '../utils/csrf';

import { PaperClipIcon } from '@heroicons/react/20/solid'

import GeneratedReportsAccordion from './GeneratedReportsAccordion';


export default function ReportItemDisplay({name, apiPathName, startDate, endDate}) {
  const queryClient = useQueryClient();


  const { isPending, error, data: reportList } = useQuery({
    queryKey: [apiPathName],
    queryFn: () =>
      fetch(`/app/v1/reports/get_by_type/${apiPathName}`).then((res) =>
        res.json(),
      ),
    enabled: true
  })

  const mutation = useMutation({
    mutationFn: () => {
      return fetch(`/app/v1/reports/generate/${apiPathName}/${getFormattedDate(startDate)}/to/${getFormattedDate(endDate)}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        }
      });
    },
    onSuccess: (responseData) => {
      console.log('Data submitted successfully:', responseData);
      // invalidate queries
      queryClient.invalidateQueries({ queryKey: [apiPathName] })
    },
    onError: (error) => {
      console.error('Error submitting data:', error);
    },
  })


  const hasReportsToList = () => {
    if (isPending) {
      return false
    }
    if (reportList.length === 0) {
      return false
    }
    return true
  }


  const getFormattedDate = (day) => {
    if (day === undefined) {
      day = dateValue.startDate
    }
    if (typeof day === 'string') {
      return day.split('T')[0]
    }
    return day
  }

  const generateReport = () => {
    mutation.mutate();
  }

  console.log(mutation)

  return <dl className="divide-y divide-gray-100">
    <p className="font-bold py-6 max-w-2xl text-sm leading-6">{name}</p>
    <div className="px-4 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-0">
      <dt className="text-sm/6 font-medium text-gray-900">
        <button
          type="button"
          className="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          onClick={generateReport}
          disabled={mutation.isPending}
        >
          {mutation.isPending ? 'Generating...' : 'Generate Report'}
        </button>
      </dt>
      <dd className="mt-1 text-sm/6 text-gray-700 sm:col-span-2 sm:mt-0">
        <GeneratedReportsAccordion
          title={`Last Generated reports for "${name}"`}
        >
          <ul role="list" className="divide-y divide-gray-100 rounded-md">
            {isPending && <span className="truncate font-medium">Loading Reports</span>}
            {(!isPending && !hasReportsToList()) &&
              <span className="truncate font-medium">No reports yet.</span>
            }
            {error && <span className="truncate font-medium">Error loading reports</span>}
            {hasReportsToList() &&
              reportList.map((report)=> {
                return <li
                  key={report.id}
                  className="flex items-center justify-between py-4 pl-4 pr-5 text-sm/6"
                >
                  <div className="flex w-0 flex-1 items-center">
                    <PaperClipIcon aria-hidden="true" className="size-5 shrink-0 text-gray-400" />
                    <div className="ml-4 flex min-w-0 flex-1 gap-2">
                      <span className="truncate font-medium">
                        Report created {getFormattedDate(report.created_at)}
                      </span>
                    </div>
                  </div>
                  <div className="ml-4 shrink-0">
                    <a href={report.report_document} className="font-medium text-indigo-600 hover:text-indigo-500">
                      Download
                    </a>
                  </div>
                </li>
              })
            }
          </ul>
        </GeneratedReportsAccordion>


      </dd>
    </div>
  </dl>
}
