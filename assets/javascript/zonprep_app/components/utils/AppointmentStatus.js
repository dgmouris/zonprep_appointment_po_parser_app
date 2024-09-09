import React, {useEffect, useState} from 'react'

import { CheckIcon } from '@heroicons/react/20/solid'

const steps = [
  { name: 'Created',
    description: 'Data Created in our system and ready to send to external fulfillment',
    href: '#',
    status: 'current',
    valid_states: ["Created"],
  },
  {
    name: 'Sent to Fulfillment',
    description: 'Sent to fulfillment and waiting for their response',
    href: '#',
    status: 'upcoming',
    valid_states: [
      "SentToFulfillment",
      "FulfillmentNotReplied",
      "FulfillmentRawAttachmentDownloaded"
    ],
  },
  { name: 'Successful OCR on Email Attachment',
    description: 'Email attachment successfully parsed and data extracted',
    href: '#',
    status: 'upcoming',
    valid_states: [
      "SuccessfulOCRAttachmentParse",
      "ErrorOCRAttachmentParse",
    ],
  },
  { name: 'Internal Appointment Info Updated',
    description: 'Internal appointment info updated from OCR in PDF',
    href: '#',
    status: 'upcoming',
    valid_states: [
      "SuccessfulAppointmentInfoUpdated",
    ],
  },
  { name: 'Internal Purchase Order Info Updated',
    description: 'Purchase Order info updated from OCR in PDF',
    href: '#',
    status: 'upcoming',
    valid_states: [
      "SuccessfulAppointmentPODataCreated",
    ],
  },
  { name: 'Data Uploaded to Salesforce',
    description: 'Data uploaded to Salesforce, process complete.',
    href: '#',
    status: 'upcoming',
    valid_states: [
      "SuccessSalesforceAppointmentDataUploaded",
      "ErrorSalesforceAppointmentDataUploaded",
    ],
  },
]

const STEPS = steps 

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export default function AppointmentStatus({appointment}) {  
  const [appointmentSteps, setAppointmentSteps] = useState(STEPS)

  const calculateStep = () => {
    const tempSteps = [...appointmentSteps]

    const currentIndex = tempSteps.findIndex(step => step.valid_states.includes(appointment.state))

    tempSteps.forEach((step, index) => {
      if (index <= currentIndex) {
        step.status = 'complete'
      } else if (index === (currentIndex  + 1)) {
        step.status = 'current'
      } else {
        step.status = 'upcoming'
      }
    })

    setAppointmentSteps(tempSteps)
  }

  useEffect(()=> {
    calculateStep()
  }, [appointment])

  return (<section className="app-card">
    <div className="px-4 sm:px-0">
        <h3 className="text-base font-semibold leading-7 text-gray-900">Current Appointment Status</h3>
        <p className="mt-1 pb-4 max-w-2xl text-sm leading-6 text-gray-500">Details on the Appointment status</p>
      </div>
    <nav aria-label="Progress">
      <ol role="list" className="overflow-hidden">
        {appointmentSteps.map((step, stepIdx) => (
          <li key={step.name} className={classNames(stepIdx !== appointmentSteps.length - 1 ? 'pb-10' : '', 'relative')}>
            {step.status === 'complete' ? (
              <>
                {stepIdx !== appointmentSteps.length - 1 ? (
                  <div aria-hidden="true" className="absolute left-4 top-4 -ml-px mt-0.5 h-full w-0.5 bg-indigo-600" />
                ) : null}
                <div href={step.href} className="group relative flex items-start">
                  <span className="flex h-9 items-center">
                    <span className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 group-hover:bg-indigo-800">
                      <CheckIcon aria-hidden="true" className="h-5 w-5 text-white" />
                    </span>
                  </span>
                  <span className="ml-4 flex min-w-0 flex-col">
                    <span className="text-sm font-medium">{step.name}</span>
                    <span className="text-sm text-gray-500">{step.description}</span>
                  </span>
                </div>
              </>
            ) : step.status === 'current' ? (
              <>
                {stepIdx !== appointmentSteps.length - 1 ? (
                  <div aria-hidden="true" className="absolute left-4 top-4 -ml-px mt-0.5 h-full w-0.5 bg-gray-300" />
                ) : null}
                <div href={step.href} aria-current="step" className="group relative flex items-start">
                  <span aria-hidden="true" className="flex h-9 items-center">
                    <span className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full border-2 border-indigo-600 bg-white">
                      <span className="h-2.5 w-2.5 rounded-full bg-indigo-600" />
                    </span>
                  </span>
                  <span className="ml-4 flex min-w-0 flex-col">
                    <span className="text-sm font-medium text-indigo-600">{step.name}</span>
                    <span className="text-sm text-gray-500">{step.description}</span>
                  </span>
                </div>
              </>
            ) : (
              <>
                {stepIdx !== appointmentSteps.length - 1 ? (
                  <div aria-hidden="true" className="absolute left-4 top-4 -ml-px mt-0.5 h-full w-0.5 bg-gray-300" />
                ) : null}
                <div href={step.href} className="group relative flex items-start">
                  <span aria-hidden="true" className="flex h-9 items-center">
                    <span className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full border-2 border-gray-300 bg-white group-hover:border-gray-400">
                      <span className="h-2.5 w-2.5 rounded-full bg-transparent group-hover:bg-gray-300" />
                    </span>
                  </span>
                  <span className="ml-4 flex min-w-0 flex-col">
                    <span className="text-sm font-medium text-gray-500">{step.name}</span>
                    <span className="text-sm text-gray-500">{step.description}</span>
                  </span>
                </div>
              </>
            )}
          </li>
        ))}
      </ol>
    </nav>
  </section>
  )
}