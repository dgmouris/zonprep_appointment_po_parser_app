import React from 'react'

import Search from './components/home/Search'
import {
  QueryClient,
  QueryClientProvider,
} from '@tanstack/react-query'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Search/>
    </QueryClientProvider>
  )
}