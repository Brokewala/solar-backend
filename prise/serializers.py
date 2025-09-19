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
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de la prise électrique'},
            'module': {'help_text': 'Module associé à cette prise'},
            'name': {'help_text': 'Nom de la prise électrique'},
            'voltage': {'help_text': 'Tension nominale de la prise (en V)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }


# PriseData
class PriseDataSerializer(serializers.ModelSerializer):
    prise = PriseSerializer(many=False, read_only=True)

    class Meta:
        model = PriseData
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique des données'},
            'prise': {'help_text': 'Prise associée à ces données'},
            'tension': {'help_text': 'Tension actuelle de la prise (en V)'},
            'puissance': {'help_text': 'Puissance actuelle de la prise (en W)'},
            'courant': {'help_text': 'Courant actuel de la prise (en A)'},
            'consomation': {'help_text': 'Consommation d\'énergie actuelle (en Wh)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }


# PrisePlanning
class PrisePlanningSerializer(serializers.ModelSerializer):
    prise = PriseSerializer(many=False, read_only=True)

    class Meta:
        model = PrisePlanning
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du planning'},
            'prise': {'help_text': 'Prise associée à ce planning'},
            'consomation': {'help_text': 'Consommation planifiée pour cette période (en Wh)'},
            'date_debut': {'help_text': 'Heure de début de la planification (format HH:MM)'},
            'date_fin': {'help_text': 'Heure de fin de la planification (format HH:MM)'},
            'date': {'help_text': 'Date de la planification'},
            'done': {'help_text': 'Indique si la planification est terminée'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

class PriseRelaiStateSerializer(serializers.ModelSerializer):
    # prise = PriseSerializer(many=False, read_only=True)

    class Meta:
        model = PriseRelaiState
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de l\'état du relais'},
            # 'prise': {'help_text': 'Prise associée à cet état'},
            'active': {'help_text': 'Indique si le relais est actif'},
            'state': {'help_text': 'État du relais (low, high)'},
            'couleur': {'help_text': 'Couleur associée à l\'état (red, green)'},
            'valeur': {'help_text': 'Valeur numérique de l\'état (0-1)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

# PriseReference
class PriseReferenceSerializer(serializers.ModelSerializer):
    prise = PriseSerializer(many=False, read_only=True)

    class Meta:
        model = PriseReference
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de la référence'},
            'prise': {'help_text': 'Prise associée à cette référence'},
            'checked_data': {'help_text': 'Indique si les données sont vérifiées'},
            'checked_state': {'help_text': 'Indique si l\'état est vérifié'},
            'duration': {'help_text': 'Durée de référence (en heures)'},
            'consommation': {'help_text': 'Consommation de référence (en Wh)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

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
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de la prise électrique'},
            'module': {'help_text': 'Module associé à cette prise'},
            'name': {'help_text': 'Nom de la prise électrique'},
            'voltage': {'help_text': 'Tension nominale de la prise (en V)'},
            'prise_data': {'help_text': 'Données de la prise'},
            'prise_planning': {'help_text': 'Planning de la prise'},
            'prise_relai_state': {'help_text': 'État du relais de la prise'},
            'prise_reference': {'help_text': 'Références de la prise'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }
