'''
The form for this view is in the dashboard because it's all at once.

please take a look at the file

apps/web/views.py

under the "home" function
'''
from datetime import datetime, time

from django.utils.html import escape
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .state import ZonprepAppointmentState, ZonprepPurchaseOrderState
from .seralizers import (ReadOnlySearchAppointmentOrPOSerializer,
                         ZonprepAppointmentSerializer,
                         ZonprepPurchaseOrderDetailSerializer,
                         ZonprepReportsSerializer,
                         ZonprepPurchaseOrderSearchSerializer,
                         ZonprepPurchaseOrderSetToSendToFullfilmmentSerializer,
                         ZonprepAppStatusSerializer,
                         TypeCEmailDetailsSerializer
                         )
from .models import ZonprepAppointment, ZonprepPurchaseOrder, ZonprepReports, TypeCEmailDetails
from .gmail_utils import GmailUtility
from .reports import Report

class ZonprepPurchaseOrderViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ZonprepPurchaseOrderDetailSerializer
    permission_classes = [IsAuthenticated]

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
            appointment = ZonprepPurchaseOrder.objects.filter(p_po_number=po_number).first()
        except ZonprepPurchaseOrder.DoesNotExist:
            raise NotFound("ZonprepPurchaseOrder with this appointment_id does not exist")
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)



class ZonprepActionViewset(viewsets.ViewSet):
    @action(
        detail=False,
        methods=['post'],
        url_path='retry_appointments_to_external_fulfillment/(?P<date>[^/.]+)'
    )
    def retry_appointments_to_external_fulfillment(self, request, date=None):
        results = []
        appts = None
        if date:
            appts = ZonprepAppointment.get_appointments_with_no_response_for_date(date)
            print(appts)
            # loop through appointments put them back in the created state.
            for appt in appts:
                appt.message_send_retried += 1
                appt.state = ZonprepAppointmentState.CREATED
                appt.save()
        else:
            # If no date is provided, return all appts or an empty list as needed
            appts = ZonprepAppointment.objects.none()
        # Serialize the filtered queryset
        result_serializer = ZonprepAppointmentSerializer(appts, many=True)
        return Response(result_serializer.data)

    @action(
        detail=False,
        methods=['post'],
        url_path='set_purchase_orders_to_be_sent'
    )
    def set_purchase_orders_to_be_sent(self, request):
        results = []
        serializer = ZonprepPurchaseOrderSetToSendToFullfilmmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # breakpoint()
        pos = []
        if serializer.data.get("search_term", None) is not None:
            pos = ZonprepPurchaseOrder.search_purchase_orders(serializer.data["search_term"])
        elif serializer.data.get("list_of_po_ids", None) is not None:
            # breakpoint()
            po_ids = [int(id) for id in serializer.data.get("list_of_po_ids", [])]

            pos = ZonprepPurchaseOrder.objects.filter(id__in=po_ids)

        # move the state over to scheduled to send to fulfillment
        for po in pos:
            if po.state == ZonprepAppointmentState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED.value:
                po.move_state_to_scheduled_to_send_to_fulfillment()
                print("moved PO {po.p_po_number} to scheduled to send to fulfillment")
        # send the state.
        return Response(serializer.data)


class ZonprepAppointmentViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = ZonprepAppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return  ZonprepAppointment.objects.all().prefetch_related('purchase_orders')

    def list(self, request, *args, **kwargs):
        # Customize the list method if needed
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, appointment_id=None, *args, **kwargs):
        # Override the retrieve method to filter by appointment_id
        try:
            appointment = ZonprepAppointment.objects.filter(
                Q(request_id=appointment_id) |
                Q(p_appointment_id=appointment_id)
            ).first()
        except ZonprepAppointment.DoesNotExist:
            raise NotFound("ZonprepAppointment with this appointment_id does not exist")
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)


class SearchAppointmentOrPOViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        search = request.query_params.get('q', None)
        # handle the case that they didn't search for anything.
        if search is None:
            empty_serializer = ReadOnlySearchAppointmentOrPOSerializer([], many=True)
            return Response(empty_serializer.data)

        # sanitize
        search = escape(search).strip().upper()

        # check if it's in the po
        appts = ZonprepAppointment.objects.filter(
            Q(request_id__contains=search) |
            Q(p_appointment_id__contains=search)
        ).prefetch_related('purchase_orders')

        pos = ZonprepPurchaseOrder.objects.filter(
            p_po_number__contains=search
        )

        # translate this to one search result list
        results = []
        # start with appointments
        for appt in appts:
            value = appt.request_id
            value_type = "request_id"
            if appt.p_appointment_id:
                value = appt.p_appointment_id
                value_type="appointment"
            results.append({
                "value": value,
                "value_type":value_type,
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
        url_path='by_purchase_order',
    )
    def search_by_purchase_order(self, request):
        search = request.query_params.get('q', None)
        search = escape(search).strip().upper()
        if search is None:
            empty_serializer = ZonprepPurchaseOrderSearchSerializer([], many=True)
            return Response(empty_serializer.data)
        purchase_orders = ZonprepPurchaseOrder.search_purchase_orders(search)
        serializer = ZonprepPurchaseOrderSearchSerializer(purchase_orders, many=True)
        return Response(serializer.data)

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
            appts = ZonprepAppointment.objects.filter(updated_at__date=date_obj).prefetch_related('purchase_orders')

            for appt in appts:
                value = appt.request_id
                value_type = "request_id"
                if appt.p_appointment_id:
                    value = appt.p_appointment_id
                    value_type="appointment"
                results.append({
                    "value": value,
                    "value_type":value_type,
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


    @action(
        detail=False,
        methods=['get'],
        url_path='unparsed_appointments_by_date/(?P<date>[^/.]+)'
    )
    def unparsed_appointments_by_date(self, request, date=None):
        no_response = None
        no_response_raw = request.query_params.get('no_external_fulfillment_response', None)
        if no_response_raw:
            no_response = no_response_raw.lower() == 'true'

        bad_appointment = None
        bad_appointment_states_raw = request.query_params.get('appointments_with_bad_states', None)
        if bad_appointment_states_raw:
            bad_appointment = bad_appointment_states_raw.lower() == 'true'

        # Get the 'date' query parameter from the request
        results = []
        if date:
            # Filter appointments based on the provided date
            appts = []
            if no_response:
                appts = ZonprepAppointment.get_appointments_with_no_response_for_date(date)
            elif bad_appointment:
                appts = ZonprepAppointment.get_appointments_with_bad_states_for_date(date)


            for appt in appts:
                value = appt.request_id
                value_type = "request_id"
                if appt.p_appointment_id:
                    value = appt.p_appointment_id
                    value_type="appointment"

                results.append({
                    "value": value,
                    "value_type":value_type,
                    "state":appt.state,
                    "updated":appt.updated_at,
                    "created":appt.created_at,
                    "extra_info": F"Tried {appt.message_send_retried + 1} time(s) to send message to fulfillment"
                })
        else:
            # If no date is provided, return all appts or an empty list as needed
            appts = ZonprepAppointment.objects.none()

        # Serialize the filtered queryset
        result_serializer = ReadOnlySearchAppointmentOrPOSerializer(data=results, many=True)
        result_serializer.is_valid(raise_exception=True)
        return Response(result_serializer.data)


class ZoneprepReportsViewset(viewsets.ModelViewSet):
    serializer_class = ZonprepReportsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return  ZonprepReports.objects.all()

    def list(self, request, *args, **kwargs):
        # Customize the list method if needed
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, report_id=None, *args, **kwargs):
        # Override the retrieve method to filter by report_id
        try:
            report = ZonprepReports.objects.filter(report_id=report_id).first()
        except ZonprepReports.DoesNotExist:
            raise NotFound("ZonprepReports with this report_id does not exist")
        serializer = self.get_serializer(report)
        return Response(serializer.data)


    @action(
        detail=False,
        methods=['post'],
        url_path='generate/(?P<report_name>[^/.]+)/(?P<start_date>[^/.]+)/to/(?P<end_date>[^/.]+)'
    )
    def average_pallet_count_per_scac(self, request, report_name=None, start_date=None, end_date=None):
        start = datetime.combine(datetime.strptime(start_date, "%Y-%m-%d").date(), time.min)
        end = datetime.combine(datetime.strptime(end_date, "%Y-%m-%d").date(), time.max)

        # get the report
        report_factory = Report.get_report(report_name)
        report_factory.generate_report(start, end)

        report = report_factory.save_report()
        serializer = self.get_serializer(report)

        return Response(serializer.data)


    @action(
        detail=False,
        methods=["get"],
        url_path="get_by_type/(?P<report_type>[^/.]+)"
    )
    def get_by_type(self, request, report_type=None):
        try:
            report = ZonprepReports.objects.filter(report_type=report_type)
        except ZonprepReports.DoesNotExist:
            raise NotFound("ZonprepReports with this report_type does not exist")
        serializer = self.get_serializer(report, many=True)
        return Response(serializer.data)


class ZonprepAppStatusViewset(viewsets.ViewSet):
    serializer_class = ZonprepAppStatusSerializer

    @action(
        detail=False,
        methods=['get'],
        url_path='current'
    )
    def current(self, request):
        appointment_in_queue = ZonprepAppointment.objects.filter(
            state=ZonprepAppointmentState.CREATED
        ).count()
        purchase_orders_in_queue = ZonprepPurchaseOrder.objects.filter(
            state=ZonprepPurchaseOrderState.SCHEDULED_TO_SEND_TO_FULFILLMENT
        ).count()
        appt_count = ZonprepAppointment.objects.filter(
            state=ZonprepAppointmentState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
        ).count()
        time_threshold = timezone.now() - timedelta(hours=24)
        appt_count_24 = ZonprepAppointment.objects.filter(
           updated_at__gte=time_threshold
        ).count()
        purchase_order_count = ZonprepPurchaseOrder.objects.filter(
            state=ZonprepPurchaseOrderState.SUCCESS_SALESFORCE_APPOINTMENT_DATA_UPLOADED
        ).count()
        purchase_order_count_24 = ZonprepPurchaseOrder.objects.filter(
            updated_at__gte=time_threshold
        ).count()

        serializer = self.serializer_class(data={
            "apointment_in_queue_count": appointment_in_queue,
            "purchase_order_in_queue_count": purchase_orders_in_queue,
            "appointment_count": appt_count,
            "appointment_count_updated_in_last_day": appt_count_24,
            "purchase_order_count": purchase_order_count,
            "purchase_order_count_updated_in_last_day": purchase_order_count_24
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class TypeCEmailDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = TypeCEmailDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TypeCEmailDetails.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def retrieve(self, request, email_id=None, *args, **kwargs):
        queryset = self.get_queryset().first()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = TypeCEmailDetails.load()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        instance = TypeCEmailDetails.load()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
