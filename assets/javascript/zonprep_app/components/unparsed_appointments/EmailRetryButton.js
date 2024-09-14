import React from 'react'

import { useQueryClient, useMutation } from '@tanstack/react-query';
import { getCSRFToken } from '../utils/csrf';



export default function EmailRetryButton({date}) {

  const queryClient = useQueryClient();

  const retryAppointmentPostRequest = async () => {
    console.log('retryAppointmentPostRequest');
    const response = await fetch(`/app/v1/actions/retry_appointments_to_external_fulfillment/${date}`, {method: "POST"});
    return response.data;
  };
  // // this is a mutation.
  const mutation = useMutation({
    mutationFn: () => {
      return fetch(`/app/v1/actions/retry_appointments_to_external_fulfillment/${date}/`, {
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
      queryClient.invalidateQueries({ queryKey: ['unparsed_appointments_by_date'] })
    },
    onError: (error) => {
      console.error('Error submitting data:', error);
    },
  });

  const handleClick = () => {
    mutation.mutate();
  }

  return <button
    type="button"
    className="block mt-2 rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
    onClick={handleClick}
  >
    Resend To External Fulfillment
  </button>
}