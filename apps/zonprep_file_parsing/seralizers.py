from rest_framework import serializers

from .models import ZonprepAppointment, ZonprepPurchaseOrder

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


class ZonprepAppointmentSerializer(serializers.ModelSerializer):
    purchase_orders = ZonprepPurchaseOrderSerializer(many=True)
    class Meta:
        model = ZonprepAppointment
        fields = '__all__'  # Include all fields from the model
