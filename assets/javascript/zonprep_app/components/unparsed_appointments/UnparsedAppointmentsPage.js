import React, {useState, useEffect} from 'react'
import {
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom';

import AppointmentParsedDataDisplay from './AppointmentParsedDataDisplay'
import AppointmentDatePicker from './AppointmentDatePicker'
import SearchResults from '../home/search_utils/SearchResults'
import EmailRetryButton from './EmailRetryButton'

export default function UnparsedAppointmentsPage() {
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

  const [dateValue, setDateValue] = useState({
    startDate: getDateFromUrlOrYesterday(),
    endDate: getDateFromUrlOrYesterday()
  });

  const queryClient = useQueryClient();

  // get the appointments that haven't gotten a response from external fulfillment.
  const { isPending, error, data: appointmentsWithNoResponseData } = useQuery({
    queryKey: ['unparsed_appointments_by_date'],
    queryFn: () =>
      fetch(`/app/v1/search/unparsed_appointments_by_date/${getFormattedDate()}/?no_external_fulfillment_response=True`).then((res) =>
        res.json(),
      ),
    enabled: true
  })

  // get appointments with bad states.
  const { isPending: isPendingBadStates, error: errorBadStates ,data: appointmentsWithBadStatesData } = useQuery({
    queryKey: ['unparsed_bad_states_appointments_by_date'],
    queryFn: () =>
      fetch(`/app/v1/search/unparsed_appointments_by_date/${getFormattedDate()}/?appointments_with_bad_states=True`).then((res) =>
        res.json(),
      ),
    enabled: true
  })

  useEffect(() => {
    // whenever the date changes, we need to refetch the data.
    queryClient.invalidateQueries({ queryKey: ['unparsed_appointments_by_date'] })
    queryClient.invalidateQueries({ queryKey: ['unparsed_bad_states_appointments_by_date'] })
    replaceCurrentPath()
  }, [dateValue])

  const replaceCurrentPath = ()=> {
    const currentPath = window.location.hash
    // remove old query param of the day.
    const currentPathWithoutQuery = currentPath.split('?')[0];
    const day = getFormattedDate()
    window.history.replaceState(null, "Unparsed Appointments for " + day, currentPathWithoutQuery + "?date=" + day)
  }

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

  const appointmentsWithIssuesExist = () => {
    if (!appointmentsWithBadStatesData) {
      return false
    }
    return appointmentsWithBadStatesData.length > 0
  }

  return <div>
      <div className="flex flex-col md:flex-row  md:gap-4">
        <div className="w-full md:w-2/3">
          <section className="app-card">
            <div className="px-4 sm:px-0">
              <h2 className="text-base font-semibold leading-7 text-gray-900">Unparsed Appointments for {getFormattedDateLabel()}</h2>
              <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">The following appointments havent been parsed.
                {getFormattedDate() === getFormattedDate(TODAY) &&
                  <>
                    <br/>
                    You might want to wait until tomorrow to for a response from external fulfillment.
                  </>
                }
              </p>
            </div>
            {/* Fix this later create the endpoint for it
              <AppointmentParsedDataDisplay />
            */}
            <h3 className="mt-4 text-base font-semibold leading-7 text-gray-900">Appointments with No Response from Fulfillment</h3>
            <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">
              The following appointments havent been parsed, most likely for not recieving a correct response from external fulfillment.
            </p>
            { error && <p>Error: {error.message}</p>}
            { appointmentsWithNoResponseData &&
              <SearchResults
                data={appointmentsWithNoResponseData}
                searchTerm={"throwawaytext"}
                loading={isPending}
                noResultsMessage={"All requests received a response, nothing to see here."}
              />
            }

            { appointmentsWithIssuesExist() &&
              <div>
                <h3 className="mt-4 text-base font-semibold leading-7 text-gray-900">Appointments with Issues to resolve</h3>
                <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">
                  The following appointments have issues that need to be resolved.<br/>

                  {getFormattedDate() === getFormattedDate(TODAY) &&
                    `IMPORTANT: This list may give you false positives, please check for tomorrow`
                  }
                </p>
                { errorBadStates && <p>Error: {errorBadStates.message}</p>}
                { appointmentsWithBadStatesData &&
                  <SearchResults
                    data={appointmentsWithBadStatesData}
                    searchTerm={"throwawaytext"}
                    loading={isPendingBadStates}
                    noResultsMessage={"No issues with appointments, nothing to see here."}
                  />
                }
              </div>
            }

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
              <EmailRetryButton date={getFormattedDate()}/>
              {/*
              Note this is something I want to add so I'm keeping the placeholder
              <button
                type="button"
                className="block mt-2 rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
              >
                Try to Parse Again
              </button> */}
            </div>
          </section>
        </div>
    </div>
  </div>
}