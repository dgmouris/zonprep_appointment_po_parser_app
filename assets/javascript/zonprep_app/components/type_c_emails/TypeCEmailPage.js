import React, {useState, useEffect} from 'react'


import {
  useQuery, useQueryClient, useMutation
} from '@tanstack/react-query'

import { getCSRFToken } from '@/components//utils/csrf';
import { useNotification } from '@/components/utils/notifications/AppNotification';




export default function TypeCEmailPage() {
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')

  const showNotification = useNotification();

  const queryClient = useQueryClient();

  const { isPending, error, data } = useQuery({
    queryKey: ['type-c-email'],
    queryFn: () => {
      return fetch(`/app/v1/type-c-emails/`).then((res) =>
        res.json(),
      )
    },
  })

  useEffect(() => {
    if (isPending) {
      return
    }
    if (!data) {
      return
    }
    setSubject(data.email_subject)
    setBody(data.email_body)
  }, [data])

  const mutation = useMutation({
    mutationFn: (newData) => {
      return fetch(`/app/v1/type-c-emails/`, {
        method: 'POST',
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
          email_subject: subject,
          email_body: body
        })
      })
    },
    onSuccess: (responseData) => {
      showNotification({
        title: 'Success',
        message: 'Type C Email has been updated',
        type: 'success'
      })
      queryClient.invalidateQueries({ queryKey: ['type-c-email'] })
    },
    onError: (error) => {
      showNotification({
        title: 'Error',
        message: 'There was an error updating the Type C Email',
        type: 'error'
      })
    }
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    mutation.mutate()
  }

  if (error) {
    return <div>Error: {error.message}</div>
  }

  if (isPending) {
    return <div>Loading...</div>
  }

  return <div>
    <div className="flex flex-col md:flex-row  md:gap-4">
      <div className="w-full md">
        <section className="app-card">
          <div className="px-4 sm:px-0 ">
            <h3 className="text-base font-semibold leading-7 text-gray-900">Change Type C Email Format</h3>
            <p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">
              Add a subject and email body to the Type C email, add PO_NUMBER as placeholder for po </p>
          </div>

          <form
            className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6"
            onSubmit={handleSubmit}
          >
            <div className="sm:col-span-4">
              <label htmlFor="type-c-subject" className="block text-sm/6 font-medium text-gray-900">
                Subject
              </label>
              <div className="mt-2">
                <div className="flex items-center rounded-md bg-white pl-3 outline outline-1 -outline-offset-1 outline-gray-300 focus-within:outline focus-within:outline-2 focus-within:-outline-offset-2 focus-within:outline-indigo-600">
                  <input
                    id="type-c-subject"
                    name="type-c-subject"
                    type="text"
                    className="block min-w-0 grow py-1.5 pl-1 pr-3 text-base text-gray-900 placeholder:text-gray-400 focus:outline focus:outline-0 sm:text-sm/6"
                    onChange={(e) => setSubject(e.target.value)}
                    value={subject}
                  />
                </div>
              </div>
            </div>

            <div className="col-span-full">
              <label htmlFor="type-c-body" className="block text-sm/6 font-medium text-gray-900">
                Message
              </label>
              <div className="mt-2">
                <textarea
                  id="type-c-body"
                  name="type-c-body"
                  rows={3}
                  className="block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6"
                  onChange={(e) => setBody(e.target.value)}
                  value={body}
                />
              </div>
            </div>
            <div className="col-span-full">
              <button
                type="submit"
                className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Save
              </button>
            </div>
          </form>

        </section>
      </div>

    </div>
  </div>
}
