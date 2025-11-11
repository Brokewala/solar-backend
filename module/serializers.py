# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
# model
from .models import Modules, ModulesInfo, ModulesDetail
from users.serializers import ProfilUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import ProfilUser
from django.db.models import Q


# serializer
class ModulesSerializer(serializers.ModelSerializer):
    user = ProfilUserSerializer(many=False, read_only=True)
    
    class Meta:
        model = Modules
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du module'},
            'user': {'help_text': 'Utilisateur propriétaire du module'},
            'reference_battery': {'help_text': 'Référence associée à la batterie'},
            'reference_prise': {'help_text': 'Référence associée à la prise'},
            'reference_panneau': {'help_text': 'Référence associée au panneau'},
            'active': {'help_text': 'Indique si le module est actif'},
            'activation_code': {'help_text': "Code d'activation du module"},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'activated_at': {'read_only': True, 'help_text': "Date d'activation"},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }

class ModulesSerializerIOT(serializers.ModelSerializer):
    # les composant
    battery_id = serializers.SerializerMethodField()
    panneau_id = serializers.SerializerMethodField()
    prise_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Modules
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du module'},
            'user': {'help_text': 'Utilisateur propriétaire du module'},
            'reference_battery': {'help_text': 'Référence associée à la batterie'},
            'reference_prise': {'help_text': 'Référence associée à la prise'},
            'reference_panneau': {'help_text': 'Référence associée au panneau'},
            'active': {'help_text': 'Indique si le module est actif'},
            'activation_code': {'help_text': "Code d'activation du module"},
            'createdAt': {'read_only': True, 'help_text': 'Date de création'},
            'activated_at': {'read_only': True, 'help_text': "Date d'activation"},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }
    
    def get_battery_id(self, obj):
        b = obj.modules_battery.first()
        return str(b.id) if b else None

    def get_panneau_id(self, obj):
        p = obj.modules_panneau.first()
        return str(p.id) if p else None

    def get_prise_id(self, obj):
        pr = obj.modules_prise.first()
        return str(pr.id) if pr else None

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
    reference_battery = serializers.CharField(required=False)
    reference_prise = serializers.CharField(required=False)
    reference_panneau = serializers.CharField(required=False)

    def validate(self, attrs):
        provided_references = {
            "reference_battery": attrs.get("reference_battery"),
            "reference_prise": attrs.get("reference_prise"),
            "reference_panneau": attrs.get("reference_panneau"),
        }

        filtered_references = {k: v for k, v in provided_references.items() if v}

        if not filtered_references:
            raise serializers.ValidationError("Au moins une référence doit être fournie.")

        query = Q()
        for field_name, value in filtered_references.items():
            query |= Q(**{field_name: value})

        module = (
            Modules.objects.select_related("user")
            .filter(query, active=True, user__isnull=False)
            .first()
        )

        if not module:
            raise serializers.ValidationError("Référence(s) invalide(s).")

        user: ProfilUser = module.user
        if not user.status or not user.is_verified:
            raise serializers.ValidationError("Compte utilisateur désactivé ou non vérifié.")

        refresh = RefreshToken.for_user(user)
        refresh["module_references"] = {
            "battery": module.reference_battery if module.reference_battery else None,
            "prise": module.reference_prise if module.reference_prise else None,
            "panneau": module.reference_panneau if module.reference_panneau else None,
        }
        refresh["module_id"] = str(module.id)
        refresh["kind"] = "iot"

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
        }

        return data
