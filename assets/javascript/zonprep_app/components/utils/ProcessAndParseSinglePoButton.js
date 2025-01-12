import React from 'react'

import { useQueryClient, useMutation } from '@tanstack/react-query';
import { getCSRFToken } from '@/components//utils/csrf';
import { useNotification } from '@/components/utils/notifications/AppNotification';

export default function ProcessAndParseSinglePoButton({po_number}) {
  const showNotification = useNotification();

  const queryClient = useQueryClient();

  const processMutation = useMutation({
    mutationFn: () => {
      return fetch(`/app/v1/actions/process_and_parse_po_again/${po_number}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
      }).then((res) => res.json())
    },
    onSuccess: (data) => {
      showNotification({
        title: 'Success',
        description: 'Processed and Parsed Purchase Order',
        type: 'success',
      });
      queryClient.invalidateQueries('purchase_order');
    },
    onError: (error) => {
      showNotification({
        title: 'Error',
        description: 'There was an error processing and parsing the Purchase Order',
        type: 'error',
      });
    }
  })


  const executeParsing = () => {
    processMutation.mutate();
  }

  return (
    <button
      type="button"
      className="rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
      onClick={executeParsing}
      disabled={processMutation.isPending}
    >
      {processMutation.isPending ?
        'Processing... This might take a few moments.'
        :
        `Try Processing and Parsing "${po_number}" again.`}
    </button>
  );
}
