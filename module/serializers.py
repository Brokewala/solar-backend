# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
# model
from .models import Modules, ModulesInfo, ModulesDetail
from users.serializers import ProfilUserSerializer


# serializer
class ModulesSerializer(serializers.ModelSerializer):
    user = ProfilUserSerializer(many=False, read_only=True)
    class Meta:
        model = Modules
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du module'},
            'user': {'help_text': 'Utilisateur propriétaire du module'},
            'reference': {'help_text': 'Référence du module'},
            'identifiant': {'help_text': 'Identifiant unique du module'},
            'password': {'help_text': 'Mot de passe du module'},
            'active': {'help_text': 'Indique si le module est actif'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

# ModulesInfo
class ModulesInfoSerializer(serializers.ModelSerializer):
    module = ModulesSerializer(many=False, read_only=True)
    class Meta:
        model = ModulesInfo
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique des informations'},
            'module': {'help_text': 'Module associé à ces informations'},
            'name': {'help_text': 'Nom du module'},
            'description': {'help_text': 'Description détaillée du module'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

# ModulesDetail
class ModulesDetailSerializer(serializers.ModelSerializer):
    module_info = ModulesInfoSerializer(many=False, read_only=True)
    class Meta:
        model = ModulesDetail
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du détail'},
            'module_info': {'help_text': 'Informations du module associées'},
            'value': {'help_text': 'Valeur du détail'},
            'description': {'help_text': 'Description du détail'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }
