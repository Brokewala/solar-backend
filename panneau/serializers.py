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
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du panneau solaire'},
            'module': {'help_text': 'Module associé à ce panneau'},
            'marque': {'help_text': 'Marque du fabricant du panneau'},
            'puissance': {'help_text': 'Puissance nominale du panneau (en W ou kW)'},
            'voltage': {'help_text': 'Tension nominale du panneau (en V)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }


# PanneauData
class PanneauDataSerializer(serializers.ModelSerializer):
    panneau = PanneauSerializer(many=False, read_only=True)

    class Meta:
        model = PanneauData
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique des données'},
            'panneau': {'help_text': 'Panneau associé à ces données'},
            'tension': {'help_text': 'Tension actuelle du panneau (en V)'},
            'puissance': {'help_text': 'Puissance actuelle du panneau (en W)'},
            'courant': {'help_text': 'Courant actuel du panneau (en A)'},
            'production': {'help_text': 'Production d\'énergie actuelle (en Wh)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

class PanneauDataSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = PanneauData
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique des données'},
            'panneau': {'help_text': 'Panneau associé à ces données'},
            'tension': {'help_text': 'Tension actuelle du panneau (en V)'},
            'puissance': {'help_text': 'Puissance actuelle du panneau (en W)'},
            'courant': {'help_text': 'Courant actuel du panneau (en A)'},
            'production': {'help_text': 'Production d\'énergie actuelle (en Wh)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }


# PanneauPlanning
class PanneauPlanningSerializer(serializers.ModelSerializer):
    panneau = PanneauSerializer(many=False, read_only=True)

    class Meta:
        model = PanneauPlanning
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du planning'},
            'panneau': {'help_text': 'Panneau associé à ce planning'},
            'energie': {'help_text': 'Énergie planifiée pour cette période (en Wh)'},
            'date_debut': {'help_text': 'Date et heure de début de la planification'},
            'date_fin': {'help_text': 'Date et heure de fin de la planification'},
            'done': {'help_text': 'Indique si la planification est terminée'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

class PanneauRelaiStateSerializer(serializers.ModelSerializer):
    # panneau = PanneauSerializer(many=False, read_only=True)

    class Meta:
        model = PanneauRelaiState
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de l\'état du relais'},
            # 'panneau': {'help_text': 'Panneau associé à cet état'},
            'active': {'help_text': 'Indique si le relais est actif'},
            'state': {'help_text': 'État du relais (low, high)'},
            'couleur': {'help_text': 'Couleur associée à l\'état (red, green)'},
            'valeur': {'help_text': 'Valeur numérique de l\'état (0-1)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

# PanneauReference
class PanneauReferenceSerializer(serializers.ModelSerializer):
    panneau = PanneauSerializer(many=False, read_only=True)

    class Meta:
        model = PanneauReference
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de la référence'},
            'panneau': {'help_text': 'Panneau associé à cette référence'},
            'checked_data': {'help_text': 'Indique si les données sont vérifiées'},
            'checked_state': {'help_text': 'Indique si l\'état est vérifié'},
            'duration': {'help_text': 'Durée de référence (en heures)'},
            'energy': {'help_text': 'Énergie de référence (en Wh)'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

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
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du panneau solaire'},
            'module': {'help_text': 'Module associé à ce panneau'},
            'marque': {'help_text': 'Marque du fabricant du panneau'},
            'puissance': {'help_text': 'Puissance nominale du panneau (en W ou kW)'},
            'voltage': {'help_text': 'Tension nominale du panneau (en V)'},
            'panneau_data': {'help_text': 'Données du panneau'},
            'panneau_planning': {'help_text': 'Planning du panneau'},
            'panneau_relai_state': {'help_text': 'État du relais du panneau'},
            'panneau_reference': {'help_text': 'Références du panneau'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }
