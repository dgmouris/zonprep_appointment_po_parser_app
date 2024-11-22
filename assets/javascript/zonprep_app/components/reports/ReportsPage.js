import React, {useState} from 'react'
import {
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom';

import DateRangePicker from './DateRangePicker';
import ReportItemDisplay from './ReportItemDisplay';

const REPORT_TYPES = [
  {
    name: "Average Pallet Count for SCAC",
    apiPathName: "average_pallet_count_per_scac"
  },
  {
    name: "Vendor code, count of unique appointments containing that vendor code",
    apiPathName: "unique_vendor_code_per_appointment_count"
  }
]


export default function ReportsPage() {
  const TODAY_DT = new Date();
  const TODAY = new Date(TODAY_DT.setDate(TODAY_DT.getDate()))
  const YESTERDAY = new Date(TODAY_DT.setDate(TODAY_DT.getDate() - 1))

  const [searchParams] = useSearchParams();

  const dateFromUrl = searchParams.get('date')

  // just to initialize the start date from the url.
  const getDateFromUrlOrYesterday = () => {
    if (dateFromUrl) {
      // need to add this for silly bug.
      const TIME_FOR_DATE = "T00:00:00"
      return new Date(`${dateFromUrl}${TIME_FOR_DATE}`)
    } else {
      return YESTERDAY
    }
  }

  const getNinetyDaysFromDate = (date) => {
    let newDate = new Date(date)
    return new Date(newDate.setDate(newDate.getDate() - 90));
  }

  const [dateValue, setDateValue] = useState({
    startDate: getNinetyDaysFromDate(getDateFromUrlOrYesterday()),
    endDate: getDateFromUrlOrYesterday()
  });

  return (
    <div>
      <div className="flex flex-col md:flex-row  md:gap-4">
        <div className="w-full md">
          <section className="app-card">
            <div className="px-4 sm:px-0 ">
              <h3 className="text-base font-semibold leading-7 text-gray-900">Generate Reports</h3>
              <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">Pick a date range and click generate reports</p>
            </div>

            <div className="mt-6">
              <DateRangePicker
                dateValue={dateValue}
                setDateValue={setDateValue}
              />
            </div>
            <div className="mt-4">

              <h3 className="block text-sm/6 font-semibold text-gray-900">Report Types</h3>
              <div className="mt-2 px-4 sm:px-0 border-t border-gray-100">
                {REPORT_TYPES.map((report, index)=> {
                  return <ReportItemDisplay
                    key={index}
                    name={report.name}
                    apiPathName={report.apiPathName}
                    startDate={dateValue.startDate}
                    endDate={dateValue.endDate}
                  />
                })}
              </div>
            </div>
          </section>
        </div>
      </div>
      <div className="flex flex-col md:flex-row  md:gap-4">

      </div>
    </div>
  )
}