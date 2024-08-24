'''
The form for this view is in the dashboard because it's all at once.

please take a look at the file 

apps/web/views.py

under the "home" function
'''
from datetime import datetime

from django.utils.html import escape
from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from .seralizers import (ReadOnlySearchAppointmentOrPOSerializer,
                         ZonprepAppointmentSerializer,
                         ZonprepPurchaseOrderSerializer)
from .models import ZonprepAppointment, ZonprepPurchaseOrder


class ZonprepPurchaseOrderViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ZonprepPurchaseOrderSerializer

    def get_queryset(self):
        return  ZonprepPurchaseOrder.objects.all()

    def list(self, request, *args, **kwargs):
        # Customize the list method if needed
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, po_number=None, *args, **kwargs):
        # Override the retrieve method to filter by p_po_number
        try:
            appointment = ZonprepPurchaseOrder.objects.get(p_po_number=po_number)
        except ZonprepPurchaseOrder.DoesNotExist:
            raise NotFound("ZonprepPurchaseOrder with this appointment_id does not exist")
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)


class ZonprepAppointmentViewset(viewsets.ReadOnlyModelViewSet):

    serializer_class = ZonprepAppointmentSerializer

    def get_queryset(self):
        return  ZonprepAppointment.objects.all()

    def list(self, request, *args, **kwargs):
        # Customize the list method if needed
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, appointment_id=None, *args, **kwargs):
        # Override the retrieve method to filter by appointment_id
        try:
            appointment = ZonprepAppointment.objects.get(appointment_id=appointment_id)
        except ZonprepAppointment.DoesNotExist:
            raise NotFound("ZonprepAppointment with this appointment_id does not exist")
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)


class SearchAppointmentOrPOViewset(viewsets.ViewSet):

    def list(self, request):
        search = request.query_params.get('q', None)
        # handle the case that they didn't search for anything.
        if search is None:
            empty_serializer = ReadOnlySearchAppointmentOrPOSerializer([], many=True)
            return Response(empty_serializer.data)
        
        # sanitize
        search = escape(search)

        # check if it's in the po
        appts = ZonprepAppointment.objects.filter(
            appointment_id__contains=search
        )

        pos = ZonprepPurchaseOrder.objects.filter(
            p_po_number__contains=search   
        )

        # translate this to one search result list
        results = []
        # start with appointments
        for appt in appts:
            results.append({
                "value": appt.appointment_id,
                "value_type":"appointment",
                "state":appt.state,
                "updated":appt.updated_at,
                "created":appt.created_at,
            })

        # next do the pos
        for po in pos:
            results.append({
                "value":po.p_po_number,
                "value_type":"purchase_order",
                "state":po.state,
                "updated":po.updated_at,
                "created":po.created_at,
            })

        # setup serializer
        result_serializer = ReadOnlySearchAppointmentOrPOSerializer(data=results, many=True)
        result_serializer.is_valid(raise_exception=True)
        return Response(result_serializer.data)


    @action(
        detail=False,
        methods=['get'],
        url_path='appointments_by_date/(?P<date>[^/.]+)'
    )
    def appointments_by_date(self, request, date=None):
        # Get the 'date' query parameter from the request
        results = []
        if date:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            # Filter appointments based on the provided date
            appts = ZonprepAppointment.objects.filter(updated_at__date=date_obj)

            for appt in appts:
                results.append({
                    "value": appt.appointment_id,
                    "value_type":"appointment",
                    "state":appt.state,
                    "updated":appt.updated_at,
                    "created":appt.created_at,
                })
        else:
            # If no date is provided, return all appts or an empty list as needed
            appts = ZonprepAppointment.objects.none()

        # Serialize the filtered queryset
        result_serializer = ReadOnlySearchAppointmentOrPOSerializer(data=results, many=True)
        result_serializer.is_valid(raise_exception=True)
        return Response(result_serializer.data)
