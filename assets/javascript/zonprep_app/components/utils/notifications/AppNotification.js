import React, { useEffect, useState, useContext, createContext  } from 'react'
import { Transition } from '@headlessui/react'
import { CheckCircleIcon } from '@heroicons/react/24/outline'
import { XMarkIcon } from '@heroicons/react/20/solid'

export const AppNotificationContext = createContext({})

export function useNotification() {
  const context = useContext(AppNotificationContext)
  if (!context) {
    throw new Error(`useCount must be used within a AppNotification`)
  }
  return context
}

export default function AppNotification({children}) {
  const [show, setShow] = useState(false)
  const [title, setTitle] = useState('')
  const [type, setType] = useState('')
  const [description, setDescription] = useState('')

  const showNotification = ({title, description, type}) => {
    setTitle(title)
    setDescription(description)
    setType(type)
    // display the message
    setShow(true)
  }

  // Set a timeout to update the state after 3 seconds
  useEffect(() => {
    // Set a timeout to update the state after 3 seconds
    const timer = setTimeout(() => {
      setShow(false)
    }, 3000);

    // Cleanup the timeout if the component unmounts
    return () => clearTimeout(timer);
  }, [show]);

  const getIcon = () => {
    if (type === 'success') {
      return <CheckCircleIcon aria-hidden="true" className="size-6 text-green-400" />
    } else if (type === 'error') {
      return <XMarkIcon aria-hidden="true" className="size-6 text-red-400" />
    }
  }

  return (
    <AppNotificationContext.Provider value={showNotification}>
      {/* Global notification live region, render this permanently at the end of the document */}
      {children}
      <div
        aria-live="assertive"
        className="pointer-events-none fixed inset-0 flex items-end px-4 py-6 sm:items-start sm:p-6"
      >
        <div className="flex w-full flex-col items-center space-y-4 sm:items-end">
          {/* Notification panel, dynamically insert this into the live region when it needs to be displayed */}
          <Transition show={show}>
            <div className="pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg bg-white shadow-lg ring-1 ring-black/5 transition data-[closed]:data-[enter]:translate-y-2 data-[enter]:transform data-[closed]:opacity-0 data-[enter]:duration-300 data-[leave]:duration-100 data-[enter]:ease-out data-[leave]:ease-in data-[closed]:data-[enter]:sm:translate-x-2 data-[closed]:data-[enter]:sm:translate-y-0">
              <div className="p-4">
                <div className="flex items-start">
                  <div className="shrink-0">
                    {getIcon()}
                  </div>
                  <div className="ml-3 w-0 flex-1 pt-0.5">
                    <p className="text-sm font-medium text-gray-900">
                      {title}
                    </p>
                    <p className="mt-1 text-sm text-gray-500">
                      {description}
                    </p>
                  </div>
                  <div className="ml-4 flex shrink-0">
                    <button
                      type="button"
                      onClick={() => {
                        setShow(false)
                      }}
                      className="inline-flex rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    >
                      <span className="sr-only">Close</span>
                      <XMarkIcon aria-hidden="true" className="size-5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </AppNotificationContext.Provider>
  )
}
