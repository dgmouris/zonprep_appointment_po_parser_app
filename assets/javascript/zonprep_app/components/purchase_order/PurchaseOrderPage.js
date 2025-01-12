import React from 'react'

import { useParams } from 'react-router-dom';

import {
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import PurchaseOrderInfoDisplay from './PurchaseOrderInfoDisplay';
import PurchaseOrderStatus from '../utils/PurchaseOrderStatus';
import PurchaseOrderSKUTable from './PurchaseOrderSKUTable';

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
      <div className="flex flex-col md:flex-row  md:gap-4">
        <div className="w-full md:w-2/3">
          <PurchaseOrderInfoDisplay data={data}/>
        </div>
        <div className="w-full md:w-1/3">
          <PurchaseOrderStatus po={data} />
        </div>
      </div>
      <div className="flex flex-col md:flex-row  md:gap-4">
        <div className="w-full">
          <PurchaseOrderSKUTable
            po={data}
            skus={data.skus}
            imageAttachments={data.image_attachments}
          />
        </div>
      </div>
    </div>
  )
}