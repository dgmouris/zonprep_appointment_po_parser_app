import React from 'react'

import AppStatus from '@/components/utils/AppStatus'
import Search from './Search'
import RecentAppointments from './RecentAppointments'

export default function HomePage() {
  return (
    <>
      <AppStatus/>
      <Search/>
      <RecentAppointments />
    </>
  )
}