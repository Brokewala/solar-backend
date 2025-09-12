# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
# model
from .models import Modules, ModulesInfo, ModulesDetail
from users.serializers import ProfilUserSerializer
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import ProfilUser


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

class ModulesSerializerIOT(serializers.ModelSerializer):
    # les composant
    battery_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True,
        source="modules_battery"  
    )
    panneau_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True,
        source="modules_panneau"  
    )
    prise_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True,
        source="modules_prise"  
    )
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


# iot/serializers.py

class IoTModuleTokenSerializer(serializers.Serializer):
    reference = serializers.CharField()

    def validate(self, attrs):
        ref = attrs.get("reference")

        module = (
            Modules.objects.select_related("user")
            .filter(reference=ref, active=True, user__isnull=False)
            .first()
        )
        if not module:
            raise serializers.ValidationError("Référence ou secret invalide.")

        user: ProfilUser = module.user
        # vérifs cohérentes avec ton CustomTokenObtainPairSerializer
        if not user.status or not user.is_verified:
            raise serializers.ValidationError("Compte utilisateur désactivé ou non vérifié.")

        refresh = RefreshToken.for_user(user)
        # Ajoute des claims utiles pour tracer côté API
        refresh["module_reference"] = module.reference
        refresh["module_id"] = str(module.id)
        refresh["kind"] = "iot"

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user":{"id":user.id},
        }

        return data
