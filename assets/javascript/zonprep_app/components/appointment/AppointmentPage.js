import React from 'react';

import { useParams } from 'react-router-dom';
import {
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import AppointmentInfoDisplay from './AppointmentInfoDisplay';


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

    <AppointmentInfoDisplay data={data}/>
  </div>


}