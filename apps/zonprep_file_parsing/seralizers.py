from rest_framework import serializers

from .models import (ZonprepAppointment, ZonprepPurchaseOrder,
                     ZonprepPurchaseOrderSKU, ZonprepPOImageAttachments,
                     ZonprepReports)

class ReadOnlySearchAppointmentOrPOSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)
    value_type = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255)
    updated = serializers.DateTimeField()
    created = serializers.DateTimeField()
    # this info will be shown in the middle of the search result row on the front end.
    # flexible and vague on purpose.
    extra_info = serializers.CharField(required=False, allow_blank=True)


class ZonprepPurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonprepPurchaseOrder
        fields = '__all__'  # Include all fields from the model

    # i don't skus to be included in the serializer
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the field you want to exclude
        self.fields.pop('skus', None)

class ZonprepAppointmentSerializer(serializers.ModelSerializer):
    purchase_orders = ZonprepPurchaseOrderSerializer(many=True)
    class Meta:
        model = ZonprepAppointment
        fields = '__all__'  # Include all fields from the model

class ZonprepPurchaseOrderSKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonprepPurchaseOrderSKU
        fields = '__all__'  # Include all fields from the model

class ZonprepPurchaseOrderSKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonprepPurchaseOrderSKU
        fields = '__all__'  # Include all fields from the model

class ZonprepPOImageAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonprepPOImageAttachments
        fields = '__all__'  # Include all fields from the model


class ZonprepPurchaseOrderDetailSerializer(serializers.ModelSerializer):
    skus = ZonprepPurchaseOrderSKUSerializer(many=True)
    image_attachments = ZonprepPOImageAttachmentsSerializer(many=True)
    class Meta:
        model = ZonprepPurchaseOrder
        fields = '__all__'  # Include all fields from the model


class ZonprepReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonprepReports
        fields = '__all__'  # Include all fields from the model

class ZonprepAppointmentSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonprepAppointment
        fields = [
            "id",
            "request_id",
            "state",
            "fc_code",
            "p_appointment_date",
            "p_appointment_id",
            "p_appointment_type",
            "p_carrier",
            "p_carrier_request_delivery_date",
            "p_cartons",
            "p_actual_arrival_date",
            "p_dock_door",
            "p_freight_terms",
            "p_scac",
            "p_pallets",
            "p_percent_needed",
            "p_priority_type",
            "p_trailer_number",
            "p_truck_location",
            "p_units",
        ]

class ZonprepPurchaseOrderSearchSerializer(serializers.ModelSerializer):
    appointment = ZonprepAppointmentSearchSerializer()
    class Meta:
        model = ZonprepPurchaseOrder
        fields = '__all__'  # Include all fields from the model
        depth = 1


class ZonprepPurchaseOrderSetToSendToFullfilmmentSerializer(serializers.Serializer):
    search_term = serializers.CharField(required=False, allow_null=True)
    list_of_po_ids = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True
    )


class ZonprepAppStatusSerializer(serializers.Serializer):
    apointment_in_queue_count = serializers.IntegerField()
    purchase_order_in_queue_count = serializers.IntegerField()
    appointment_count = serializers.IntegerField()
    appointment_count_updated_in_last_day = serializers.IntegerField()
    purchase_order_count = serializers.IntegerField()
    purchase_order_count_updated_in_last_day = serializers.IntegerField()
