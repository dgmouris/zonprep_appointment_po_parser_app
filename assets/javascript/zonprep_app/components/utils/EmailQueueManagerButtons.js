import React, {useState} from 'react';

import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';

import { getCSRFToken } from '@/components//utils/csrf';

import { useNotification } from '@/components/utils/notifications/AppNotification';

export default function EmailQueueManagerButtons() {
  const showNotification = useNotification();
  const queryClient = useQueryClient();

  const { isPending, error, data } = useQuery({
    queryKey: ['email_queue_status'],
    queryFn: () => {
      return fetch(`/app/v1/app-status/email_queue_status/`).then((res) =>
        res.json(),
      )
    }
  })

  const toggleEmailMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/app/v1/actions/toggle_email_queue/`, {
        method: 'POST',
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        }
      })
      return response.json()
    },
    onMutate: () => {
      queryClient.invalidateQueries({ queryKey: ['email_queue_status'] })
    },
    onError: (error) => {
      showNotification({
        title: 'Error toggling email queue',
        description: 'There was an error toggling the email queue',
        type: 'error'
      })
    },
    onSuccess: (data) => {
      let text = data.paused ? "paused" : "resumed"
      showNotification({
        title: `Email Queue is ${text}`,
        type: 'success'
      })
      queryClient.invalidateQueries({ queryKey: ['email_queue_status'] })
    }
  })


  const deleteEmailQueueMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/app/v1/actions/delete_email_queue/`, {
        method: 'POST',
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        }
      })
      return response.json()
    },
    onMutate: () => {
      queryClient.invalidateQueries({ queryKey: ['email_queue_status',  'current_app_status'] })
    },
    onSuccess: (data) => {
      showNotification({
        title: 'Email Queue Deleted',
        description: 'This might take a few seconds to update the application status',
        type: 'success'
      })
      queryClient.invalidateQueries({ queryKey: ['email_queue_status', 'current_app_status'] })
    },
    onError: (error) => {
      showNotification({
        title: 'Error deleting email queue',
        description: 'There was an error deleting the email queue',
        type: 'error'
      })
    }
  })

  const toggleQueue = () => {
    toggleEmailMutation.mutate()
  }

  const deleteQueue = () => {
    deleteEmailQueueMutation.mutate()
  }

  if (isPending || error) {
    return <></>
  }

  if (!data.paused) {
    return <div className="mt-2  sm:mt-0 flex">
    <button
      type="button"
      onClick={toggleQueue}
      className="rounded bg-white px-2 py-1 text-xs font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-red-300 hover:bg-red-50"
      disabled={toggleEmailMutation.isPending}
    >
      Pause Queue
    </button>
    </div>
  }

  return <div className="mt-2  sm:mt-0 flex">
    <button
      type="button"
      onClick={toggleQueue}
      className="rounded bg-white px-2 py-1 mr-2 text-xs font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-green-300 hover:bg-green-50"
      disabled={toggleEmailMutation.isPending || deleteEmailQueueMutation.isPending}
    >
      Resume Queue
    </button>
    <button
      type="button"
      onClick={deleteQueue}
      className="rounded bg-red-600 px-2 py-1 mr-2 text-xs font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600"
      disabled={toggleEmailMutation.isPending || deleteEmailQueueMutation.isPending}
    >
      {deleteEmailQueueMutation.isPending ? "Processing..." : "Delete All In Queue"}
    </button>
  </div>
}
