import React from 'react'

import { useParams } from 'react-router-dom';

import {
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import PurchaseOrderInfoDisplay from './PurchaseOrderInfoDisplay';


export default function PurchaseOrderPage() {

  const { purchaseOrderId } = useParams();

  const queryClient = useQueryClient();

  const { isPending, error, data } = useQuery({
    queryKey: ['purchase_order', purchaseOrderId],
    queryFn: () =>
      fetch(`/app/v1/purchase-orders/${purchaseOrderId}`).then((res) =>
        res.json(),
      ),
    enabled: !!purchaseOrderId
  })

  if (error) {
    return <div>Error: {error.message}</div>
  }

  if (isPending) {
    return (
      <div>
        <h1>Purchase Order Page</h1>
        <p>Purchase Order ID: {purchaseOrderId} loading...</p>
      </div>
    )
  }

  return (
    <div>
      <PurchaseOrderInfoDisplay data={data}/>
    </div>
  )
}