# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

# model
from .models import Prise
from .models import PriseData
from .models import PrisePlanning
from .models import PriseReference
from .models import PriseRelaiState
from module.serializers import ModulesSerializer


# serializer Prise
class PriseSerializer(serializers.ModelSerializer):
    module = ModulesSerializer(many=False, read_only=True)

    class Meta:
        model = Prise
        fields = "__all__"




# PriseData
class PriseDataSerializer(serializers.ModelSerializer):
    prise = PriseSerializer(many=False, read_only=True)

    class Meta:
        model = PriseData
        fields = "__all__"


# PrisePlanning
class PrisePlanningSerializer(serializers.ModelSerializer):
    prise = PriseSerializer(many=False, read_only=True)

    class Meta:
        model = PrisePlanning
        fields = "__all__"

class PriseRelaiStateSerializer(serializers.ModelSerializer):
    prise = PriseSerializer(many=False, read_only=True)

    class Meta:
        model = PriseRelaiState
        fields = "__all__"

# PriseReference
class PriseReferenceSerializer(serializers.ModelSerializer):
    prise = PriseSerializer(many=False, read_only=True)

    class Meta:
        model = PriseReference
        fields = "__all__"

# all
class PriseAllSerializer(serializers.ModelSerializer):
    module = ModulesSerializer(many=False, read_only=True)
    prise_data = PriseDataSerializer(many=True, read_only=True)
    prise_planning = PrisePlanningSerializer(many=False, read_only=True)
    prise_relai_state = PriseRelaiStateSerializer(many=False, read_only=True)
    prise_reference = PriseReferenceSerializer(many=False, read_only=True)
    
    class Meta:
        model = Prise
        fields = "__all__"
