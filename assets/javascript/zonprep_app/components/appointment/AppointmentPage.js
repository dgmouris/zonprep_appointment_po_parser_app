import React from 'react';

import { useParams } from 'react-router-dom';
import {
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import AppointmentInfoDisplay from './AppointmentInfoDisplay';
import AppointmentStatus from '../utils/AppointmentStatus';

export default function AppointmentPage() {
  const { appointmentId } = useParams();

  const queryClient = useQueryClient();
  
  const { isPending, error, data } = useQuery({
    queryKey: ['appointment', appointmentId],
    queryFn: () =>
      fetch(`/app/v1/appointments/${appointmentId}`).then((res) =>
        res.json(),
      ),
    enabled: !!appointmentId
  })


  if (error) {
    return <div>Error: {error.message}</div>
  }

  if (isPending) {
    return (
      <div>
        <h1>Appointment Page</h1>
        <p>Appointment ID: {appointmentId} loading...</p>
      </div>
    )
  }

  return <div>
      <div className="flex flex-col md:flex-row  md:gap-4">
        <div className="w-full md:w-2/3">
          <AppointmentInfoDisplay data={data}/>
        </div>
        <div className="w-full md:w-1/3">
          <AppointmentStatus appointment={data} />
        </div>
    </div>
  </div>


}
