# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

# model
from .models import Panneau
from .models import PanneauData
from .models import PanneauPlanning
from .models import PanneauReference
from .models import PanneauRelaiState
from module.serializers import ModulesSerializer


# serializer Panneau
class PanneauSerializer(serializers.ModelSerializer):
    module = ModulesSerializer(many=False, read_only=True)

    class Meta:
        model = Panneau
        fields = "__all__"


# PanneauData
class PanneauDataSerializer(serializers.ModelSerializer):
    panneau = PanneauSerializer(many=False, read_only=True)

    class Meta:
        model = PanneauData
        fields = "__all__"


# PanneauPlanning
class PanneauPlanningSerializer(serializers.ModelSerializer):
    panneau = PanneauSerializer(many=False, read_only=True)

    class Meta:
        model = PanneauPlanning
        fields = "__all__"

class PanneauRelaiStateSerializer(serializers.ModelSerializer):
    panneau = PanneauSerializer(many=False, read_only=True)

    class Meta:
        model = PanneauRelaiState
        fields = "__all__"

# PanneauReference
class PanneauReferenceSerializer(serializers.ModelSerializer):
    panneau = PanneauSerializer(many=False, read_only=True)

    class Meta:
        model = PanneauReference
        fields = "__all__"

# all
class PenneauAllSerializer(serializers.ModelSerializer):
    module = ModulesSerializer(many=False, read_only=True)
    panneau_data = PanneauDataSerializer(many=True, read_only=True)
    panneau_planning = PanneauPlanningSerializer(many=False, read_only=True)
    panneau_relai_state = PanneauRelaiStateSerializer(many=False, read_only=True)
    panneau_reference = PanneauReferenceSerializer(many=False, read_only=True)
    
    class Meta:
        model = Panneau
        fields = "__all__"
