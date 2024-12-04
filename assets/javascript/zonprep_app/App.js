import React from 'react'

import HomePage from './components/home/HomePage'
import AppointmentPage from './components/appointment/AppointmentPage';
import PurchaseOrderPage from './components/purchase_order/PurchaseOrderPage';
import UnparsedAppointmentsPage from './components/unparsed_appointments/UnparsedAppointmentsPage';
import ReportsPage from './components/reports/ReportsPage';
import PurchaseOrderToolsPage from './components/purchase_order_tools/PurchaseOrderToolsPage';

import {
  HashRouter,
  Route,
  Routes
} from "react-router-dom";
import {
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'

import AppNotification from './components/utils/notifications/AppNotification';

const queryClient = new QueryClient()

export default function App() {
  return (
    <AppNotification>
      <QueryClientProvider client={queryClient}>
        <HashRouter basename='/'>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/appointment/:appointmentId" element={<AppointmentPage />} />
            <Route path="/purchase_order/:purchaseOrderId" element={<PurchaseOrderPage />} />
            <Route path="/unparsed_appointments" element={<UnparsedAppointmentsPage />} />
            <Route path="/reports" element={<ReportsPage/>} />
            <Route path="/purchase_order_tools" element={<PurchaseOrderToolsPage/>} />
          </Routes>
        </HashRouter>
      </QueryClientProvider>
    </AppNotification>
  )
}