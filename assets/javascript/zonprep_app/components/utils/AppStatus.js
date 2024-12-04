import React from 'react'

import AppStatusStatistic from './AppStatusStatistic'

import {
  useQuery,
} from '@tanstack/react-query'

export default function AppStatus() {
  const { isPending, error, data } = useQuery({
    queryKey: ['search_purchase_orders'],
    queryFn: () => {
      return fetch(`/app/v1/app-status/current/`).then((res) =>
        res.json(),
      )
    },
    refetchInterval: 15000,
    refetchIntervalInBackground: true,
  })

  if (isPending) {
    return (
      <section className="app-card">
        <h1>App Status</h1>
        <h3 htmlFor="search" className="block text-sm font-medium leading-5 text-gray-900">
          Loading App Status...
        </h3>
      </section>
    )
  }

  if (error) {
    return <section className="app-card">
      <div>Error: {error.message}</div>
    </section>
  }

  return <section className="app-card">
    <h3 htmlFor="search" className="block text-sm font-medium leading-5 text-gray-900">
      Overview of App Status Queue
    </h3>
    <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
      <AppStatusStatistic
        title="Emails in Queue"
        value={data.apointment_in_queue_count + data.purchase_order_in_queue_count}
        description={"emails in queue"}
        detail={`${data.apointment_in_queue_count} appts and ${data.purchase_order_in_queue_count} pos`}
        />
      <AppStatusStatistic
        title="Appointments"
        value={data.appointment_count}
        description={"parsed successfully"}
        detail={`${data.appointment_count_updated_in_last_day} done today`}
      />
      <AppStatusStatistic
        title="Purchase Orders"
        value={data.purchase_order_count}
        description={"created successfully"}
        detail={`${data.purchase_order_count_updated_in_last_day} done today`}
      />
    </div>
  </section>
}