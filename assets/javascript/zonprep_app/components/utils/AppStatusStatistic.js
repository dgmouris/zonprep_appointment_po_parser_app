import React from 'react'

import Divider from './uikit/Divider'
import Badge from './uikit/Badge'

export default function AppStatusStatistic({title, description, value, detail}) {
  return  <div>
    <Divider />
    <div className="mt-4 text-lg/6 font-medium sm:text-sm/6">
      {title}
    </div>
    <div className="mt-3 text-3xl/8 font-semibold sm:text-2xl/8">
      {value}
      <span className="ml-2 text-sm font-medium text-gray-500">{description}</span>
    </div>
    <div className="mt-3 text-sm/6 sm:text-xs/6">
    <div className="mb-4">
      <Badge color="indigo" text={detail} />
    </div>
    <Divider />
    </div>
  </div>

}