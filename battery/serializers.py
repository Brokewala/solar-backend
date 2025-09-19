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
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de la batterie'},
            'module': {'help_text': 'Module associé à cette batterie'},
            'marque': {'help_text': 'Marque du fabricant de la batterie'},
            'puissance': {'help_text': 'Puissance nominale de la batterie (en W ou kW)'},
            'voltage': {'help_text': 'Tension nominale de la batterie (en V)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }


# BatteryData
class BatteryDataSerializer(serializers.ModelSerializer):
    battery = BatterySerializer(many=False, read_only=True)

    class Meta:
        model = BatteryData
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique des données'},
            'battery': {'help_text': 'Batterie associée à ces données'},
            'tension': {'help_text': 'Tension actuelle de la batterie (en V)'},
            'puissance': {'help_text': 'Puissance actuelle de la batterie (en W)'},
            'courant': {'help_text': 'Courant actuel de la batterie (en A)'},
            'energy': {'help_text': 'Énergie stockée dans la batterie (en Wh)'},
            'pourcentage': {'help_text': 'Pourcentage de charge de la batterie (%)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }


# BatteryPlanning
class BatteryPlanningSerializer(serializers.ModelSerializer):
    battery = BatterySerializer(many=False, read_only=True)

    class Meta:
        model = BatteryPlanning
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du planning'},
            'battery': {'help_text': 'Batterie associée à ce planning'},
            'energie': {'help_text': 'Énergie planifiée pour cette période (en Wh)'},
            'date_debut': {'help_text': 'Heure de début de la planification (format HH:MM)'},
            'date_fin': {'help_text': 'Heure de fin de la planification (format HH:MM)'},
            'date': {'help_text': 'Date de la planification'},
            'done': {'help_text': 'Indique si la planification est terminée'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

class BatteryRelaiStateSerializer(serializers.ModelSerializer):
    # battery = BatterySerializer(many=False, read_only=True)

    class Meta:
        model = BatteryRelaiState
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de l\'état du relais'},
            # 'battery': {'help_text': 'Batterie associée à cet état'},
            'active': {'help_text': 'Indique si le relais est actif'},
            'state': {'help_text': 'État du relais (low, medium, high)'},
            'couleur': {'help_text': 'Couleur associée à l\'état (red, orange, green)'},
            'valeur': {'help_text': 'Valeur numérique de l\'état'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

class BatteryReferenceSerializer(serializers.ModelSerializer):
    battery = BatterySerializer(many=False, read_only=True)

    class Meta:
        model = BatteryReference
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de la référence'},
            'battery': {'help_text': 'Batterie associée à cette référence'},
            'checked_data': {'help_text': 'Indique si les données sont vérifiées'},
            'checked_state': {'help_text': 'Indique si l\'état est vérifié'},
            'duration': {'help_text': 'Durée de référence (en heures)'},
            'energy': {'help_text': 'Énergie de référence (en Wh)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

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
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de la batterie'},
            'module': {'help_text': 'Module associé à cette batterie'},
            'marque': {'help_text': 'Marque du fabricant de la batterie'},
            'puissance': {'help_text': 'Puissance nominale de la batterie (en W ou kW)'},
            'voltage': {'help_text': 'Tension nominale de la batterie (en V)'},
            'battery_data': {'help_text': 'Données de la batterie'},
            'battery_planning': {'help_text': 'Planning de la batterie'},
            'battery_relai_state': {'help_text': 'État du relais de la batterie'},
            'battery_reference': {'help_text': 'Références de la batterie'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }
