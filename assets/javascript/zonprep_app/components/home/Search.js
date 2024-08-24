import React, {useState, useEffect} from 'react'

import {
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import SearchAppointmentOrPO from './search_utils/SearchAppointmentOrPO'
import SearchResults from './search_utils/SearchResults'

export default function Search() {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('')

  // search function to fetch the values, needs to be longer than 3 characters
  const { isPending, error, data } = useQuery({
    queryKey: ['search_appointment_or_po'],
    queryFn: () =>
      fetch(`/app/v1/search/?q=${searchTerm}`).then((res) =>
        res.json(),
      ),
    enabled: searchTerm.length > 3
  })

  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ['search_appointment_or_po'] })    
  }, [searchTerm])

  if (error) {
    return <div>Error: {error.message}</div>
  }
  return (
    <section class="app-card">
      <SearchAppointmentOrPO
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
      />
      <SearchResults searchTerm={searchTerm} data={data} loading={isPending}/>
    </section>
  )
}