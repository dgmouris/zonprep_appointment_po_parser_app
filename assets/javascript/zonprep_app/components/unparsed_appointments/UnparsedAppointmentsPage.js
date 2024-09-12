import React, {useState, useEffect} from 'react'

import AppointmentParsedDataDisplay from './AppointmentParsedDataDisplay'
import AppointmentDatePicker from './AppointmentDatePicker'


export default function UnparsedAppointmentsPage() {
  const TODAY_DT = new Date();
  const TODAY = new Date(TODAY_DT.setDate(TODAY_DT.getDate()))
  const YESTERDAY = new Date(TODAY_DT.setDate(TODAY_DT.getDate() - 1))

  const [dateValue, setDateValue] = useState({ 
    startDate: YESTERDAY, 
    endDate: YESTERDAY
  });


  const getFormattedDate = (day) => {
    if (day === undefined) {
      day = dateValue.startDate
    }
    return day.toISOString().split('T')[0]
  }

  const getFormattedDateLabel = () => {
    if (getFormattedDate() === getFormattedDate(YESTERDAY)) {
      return 'Yesterday'
    } else if (getFormattedDate() === getFormattedDate(TODAY)) {
      return 'Today (note maybe still be parsing)'
    } else {
      return dateValue.startDate.toDateString()
    }
  }

  return <div>
      <div className="flex flex-col md:flex-row  md:gap-4">
        <div className="w-full md:w-2/3">
            <section className="app-card">
              <div className="px-4 sm:px-0">
                <h3 className="text-base font-semibold leading-7 text-gray-900">Unparsed Appointments for {getFormattedDateLabel()}</h3>
                <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">The following appointments havent been parsed.
                  {getFormattedDate() === getFormattedDate(TODAY) &&
                    <>
                      <br/>
                      You might want to wait until tomorrow to for a response from external fulfillment.
                    </>
                  }
                </p>
              </div>
              <AppointmentParsedDataDisplay />
              <p className="mt-4 max-w-2xl text-sm leading-6 text-gray-500">
                The following appointments havent been parsed, most likely for not recieving a correct response from external fulfillment.
              </p>
            </section>
        </div>
        <div className="w-full md:w-1/3">
          <section className="app-card">
            <AppointmentDatePicker
              dateValue={dateValue}
              setDateValue={setDateValue}
            />
            <div className="mt-4">
              <h3 className="text-base font-semibold leading-6 text-gray-900">Actions</h3>
              <button
                type="button"
                className="mt-2 rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Resend To External Fulfillment
              </button>

              <button
                type="button"
                className="mt-2 rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
              >
                Try to Parse Again
              </button>
            </div>
          </section>
        </div>
    </div>
  </div>
}