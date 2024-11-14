# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

# model
from .models import Battery, BatteryData, BatteryPlanning, BatteryRelaiState
from .models import BatteryReference
from module.serializers import ModulesSerializer


# serializer
class BatterySerializer(serializers.ModelSerializer):
    module = ModulesSerializer(many=False, read_only=True)

    class Meta:
        model = Battery
        fields = "__all__"


# BatteryData
class BatteryDataSerializer(serializers.ModelSerializer):
    battery = BatterySerializer(many=False, read_only=True)

    class Meta:
        model = BatteryData
        fields = "__all__"


# BatteryPlanning
class BatteryPlanningSerializer(serializers.ModelSerializer):
    battery = BatterySerializer(many=False, read_only=True)

    class Meta:
        model = BatteryPlanning
        fields = "__all__"

class BatteryRelaiStateSerializer(serializers.ModelSerializer):
    battery = BatterySerializer(many=False, read_only=True)

    class Meta:
        model = BatteryRelaiState
        fields = "__all__"

class BatteryReferenceSerializer(serializers.ModelSerializer):
    battery = BatterySerializer(many=False, read_only=True)

    class Meta:
        model = BatteryReference
        fields = "__all__"

# all
class BatteryAllSerializer(serializers.ModelSerializer):
    module = ModulesSerializer(many=False, read_only=True)
    battery_data = BatteryDataSerializer(many=True, read_only=True)
    battery_planning = BatteryPlanningSerializer(many=False, read_only=True)
    battery_relai_state = BatteryRelaiStateSerializer(many=False, read_only=True)
    battery_reference = BatteryReferenceSerializer(many=False, read_only=True)
    
    class Meta:
        model = Battery
        fields = "__all__"
