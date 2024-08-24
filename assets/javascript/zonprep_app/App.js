import React from 'react'

import HomePage from './components/home/HomePage'
import AppointmentPage from './components/appointment/AppointmentPage';
import PurchaseOrderPage from './components/purchase_order/PurchaseOrderPage';
import { 
  HashRouter,
  Route,
  Routes
} from "react-router-dom";
import {
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <HashRouter basename='/'>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/appointment/:appointmentId" element={<AppointmentPage />} />
          <Route path="/purchase_order/:purchaseOrderId" element={<PurchaseOrderPage />} />
        </Routes>
      </HashRouter>
    </QueryClientProvider>
  )
}