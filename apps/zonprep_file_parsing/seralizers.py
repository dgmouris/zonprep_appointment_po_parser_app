from rest_framework import serializers

from .models import ZonprepAppointment, ZonprepPurchaseOrder

class ReadOnlySearchAppointmentOrPOSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)
    value_type = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255)
    updated = serializers.DateTimeField()
    created = serializers.DateTimeField()


class ZonprepAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonprepAppointment
        fields = '__all__'  # Include all fields from the model

class ZonprepPurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonprepPurchaseOrder
        fields = '__all__'  # Include all fields from the model