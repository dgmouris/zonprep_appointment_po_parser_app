import React from 'react';
import SearchResults from './search_utils/SearchResults';


import {
  useQuery,
} from '@tanstack/react-query'


export default function RecentAppointments() {
  // get todays date in a good format.
  const today = new Date().toISOString().split('T')[0];

  const { isPending, error, data } = useQuery({
    queryKey: ['recent_appointments'],
    queryFn: () =>
      fetch(`/app/v1/search/appointments_by_date/${today}/`).then((res) =>
        res.json(),
      ),
    enabled: true
  })
  console.log("RecentAppointments")
  console.log(data);
  console.log(isPending);
  console.log(error);

  if (error) {
    return <div>Error getting dates: {error.message}</div>
  }

  if (isPending) {
    return (
      <div>
        <h3 htmlFor="search" className="block text-sm font-medium leading-6 text-gray-900">
          Appointments updated in the last day.
        </h3>
        <p>loading...</p>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div>
        <h3 htmlFor="search" className="block text-sm font-medium leading-6 text-gray-900">
          Appointments updated today
        </h3>
        <p>No appointments updated today</p>
      </div>
    )
  }

  
  return (
    <div>
      <h3 htmlFor="search" className="block text-sm font-medium leading-6 text-gray-900">
        Appointments updated today
      </h3>
      <SearchResults data={data} loading={isPending}/>
    </div>
  );
}