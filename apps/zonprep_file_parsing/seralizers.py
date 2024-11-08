from rest_framework import serializers

from .models import (ZonprepAppointment, ZonprepPurchaseOrder,
                     ZonprepPurchaseOrderSKU, ZonprepPOImageAttachments)

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
