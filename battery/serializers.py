# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

# model
from .models import Battery,BatteryData,BatteryPlanning
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
