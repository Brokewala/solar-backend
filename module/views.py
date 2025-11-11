from rest_framework import status

# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# models
from .models import Modules
from .models import ModulesInfo
from .models import ModulesDetail
from users.models import ProfilUser
from prise.models import Prise
from panneau.models import Panneau
from battery.models import Battery

# serializer
from .serializers import ModulesSerializer
from .serializers import ModulesInfoSerializer
from .serializers import IoTModuleTokenSerializer
from .serializers import ModulesDetailSerializer
from .serializers import ModulesSerializerIOT


def parse_boolean(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    return str(value).lower() in ("true", "1", "yes", "on")


# Tests rapides (manuels) :
# - POST /module/modules avec un user puis PUT pour ajouter reference_battery
#   et vérifier que la réponse n'expose pas d'identifiants hérités.
# - POST /module/token/ avec au moins une référence pour obtenir un jeton.
# - GET /module/modules/by-reference/panneau/<valeur> pour récupérer un module ou obtenir un 404.


class IoTModuleTokenView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = IoTModuleTokenSerializer

    @swagger_auto_schema(
        operation_description="Génère un jeton pour un module IoT actif",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reference_battery': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée à la batterie du module', nullable=True),
                'reference_prise': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée à la prise du module', nullable=True),
                'reference_panneau': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée au panneau du module', nullable=True),
            },
        ),
        responses={
            200: openapi.Response('Jeton généré avec succès'),
            400: openapi.Response('Référence(s) invalide(s) ou compte inactif'),
        }
    )
    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        return Response(ser.validated_data)

class IoTTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


# get all module
@swagger_auto_schema(
    method='get',
    operation_description="Récupère tous les modules",
    responses={
        200: ModulesSerializer(many=True),
        400: 'Bad Request',
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_module(request):
    modules = Modules.objects.all().order_by("-createdAt")
    serializer = ModulesSerializer(modules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Crée un module complet avec batterie, panneau et prise",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'puissance_battery', 'voltage_battery', 'marque_battery', 'puissance_panneau', 'voltage_panneau', 'marque_panneau', 'name_prise', 'voltage_prise'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID de l\'utilisateur'),
            'reference_battery': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée à la batterie du module', nullable=True),
            'reference_prise': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée à la prise du module', nullable=True),
            'reference_panneau': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée au panneau du module', nullable=True),
            'puissance_battery': openapi.Schema(type=openapi.TYPE_STRING, description='Puissance de la batterie'),
            'voltage_battery': openapi.Schema(type=openapi.TYPE_STRING, description='Tension de la batterie'),
            'marque_battery': openapi.Schema(type=openapi.TYPE_STRING, description='Marque de la batterie'),
            'puissance_panneau': openapi.Schema(type=openapi.TYPE_STRING, description='Puissance du panneau'),
            'voltage_panneau': openapi.Schema(type=openapi.TYPE_STRING, description='Tension du panneau'),
            'marque_panneau': openapi.Schema(type=openapi.TYPE_STRING, description='Marque du panneau'),
            'name_prise': openapi.Schema(type=openapi.TYPE_STRING, description='Nom de la prise'),
            'voltage_prise': openapi.Schema(type=openapi.TYPE_STRING, description='Tension de la prise')
        }
    ),
    responses={
        201: ModulesSerializer,
        400: openapi.Response('Champs requis manquants'),
        500: 'Internal Server Error'
    }
)
@api_view(["POST"])
def create_module_all(request):
    user_id = request.data.get("user_id")
    reference_battery = request.data.get("reference_battery") or None
    reference_prise = request.data.get("reference_prise") or None
    reference_panneau = request.data.get("reference_panneau") or None

    # battery
    puissance_battery = request.data.get("puissance_battery")
    voltage_battery = request.data.get("voltage_battery")
    marque_battery = request.data.get("marque_battery")

    # panneau
    puissance_panneau = request.data.get("puissance_panneau")
    voltage_panneau = request.data.get("voltage_panneau")
    marque_panneau = request.data.get("marque_panneau")
    # prise
    name_prise = request.data.get("name_prise")
    voltage_prise = request.data.get("voltage_prise")

  # Check for missing or empty fields
    required_fields = {
        "user_id": user_id,
        "puissance_battery": puissance_battery,
        "voltage_battery": voltage_battery,
        "marque_battery": marque_battery,
        "puissance_panneau": puissance_panneau,
        "voltage_panneau": voltage_panneau,
        "marque_panneau": marque_panneau,
        "name_prise": name_prise,
        "voltage_prise": voltage_prise,
    }

    missing_fields = [key for key, value in required_fields.items() if not value]

    if missing_fields:
        return Response(
            {"error": "Missing or empty required fields", "fields": missing_fields},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # create module
    module = Modules.objects.create(
        user_id=user_id,
        reference_battery=reference_battery,
        reference_prise=reference_prise,
        reference_panneau=reference_panneau,
    )
        
    # craete battery
    Battery.objects.create(
        module_id=module.id,
        puissance=puissance_battery,
        voltage=voltage_battery,
        marque=marque_battery,
    )

    # create panneau
    Panneau.objects.create(
        module_id=module.id,
        puissance=puissance_panneau,
        voltage=voltage_panneau,
        marque=marque_panneau,
    )

    # create prise
    Prise.objects.create(
        module_id=module.id,
        name=name_prise,
        voltage=voltage_prise,
    )

 
    # save module
    module.save()
    serializer = ModulesSerializer(module,many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# get all module
@swagger_auto_schema(
    method='get',
    operation_description="Récupère un module par l'ID de l'utilisateur",
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_PATH,
            description="Identifiant unique de l'utilisateur",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: ModulesSerializer,
        404: openapi.Response('Module non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_module_by_user(request, user_id):
    try:
        modules = Modules.objects.get(user__id=user_id)
        serializer = ModulesSerializerIOT(modules, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Modules.DoesNotExist:
        return Response(
            {"error": "module not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
        

@swagger_auto_schema(
    method='GEt',
    operation_description="Récupère un module par l'ID de l'utilisateur pour IOT",
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_PATH,
            description="Identifiant unique de l'utilisateur IOT",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: ModulesSerializerIOT,
        404: openapi.Response('Module non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["GEt"])
# @permission_classes([IsAuthenticated])
def get_one_module_by_user_for_IOT(request, user_id):
    try:
        modules = Modules.objects.get(user__id=user_id)
        serializer = ModulesSerializerIOT(modules, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Modules.DoesNotExist:
        return Response(
            {"error": "module not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

#  get module by reference
@swagger_auto_schema(
    method='get',
    operation_description="Récupère un module par type de référence",
    manual_parameters=[
        openapi.Parameter(
            'ref_type',
            openapi.IN_PATH,
            description="Type de référence (battery, prise, panneau)",
            type=openapi.TYPE_STRING,
            enum=['battery', 'prise', 'panneau'],
            required=True
        ),
        openapi.Parameter(
            'ref_value',
            openapi.IN_PATH,
            description="Valeur de la référence du module",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: ModulesSerializer,
        404: openapi.Response('Module non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(['GET'])
def get_module_by_reference(request, ref_type, ref_value):
    reference_field_map = {
        'battery': 'reference_battery',
        'prise': 'reference_prise',
        'panneau': 'reference_panneau',
    }

    field_name = reference_field_map.get(ref_type)
    if field_name is None:
        return Response(
            {"error": "Type de référence invalide."},
            status=status.HTTP_404_NOT_FOUND
        )

    module = Modules.objects.filter(**{field_name: ref_value}).first()
    if not module:
        return Response(
            {"error": "Module not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ModulesSerializer(module)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Modules APIView
class ModulesAPIView(APIView):

    def get_object(self, module_id):
        try:
            return Modules.objects.get(id=module_id)
        except Modules.DoesNotExist:
            return Response(
                {"error": "module not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_description="Crée un nouveau module",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user'],
            properties={
                'reference_battery': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée à la batterie du module', nullable=True),
                'reference_prise': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée à la prise du module', nullable=True),
                'reference_panneau': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée au panneau du module', nullable=True),
                'activation_code': openapi.Schema(type=openapi.TYPE_STRING, description="Code d'activation du module", nullable=True),
                'active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Statut actif du module'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='ID de l\'utilisateur')
            }
        ),
        responses={
            201: ModulesSerializer,
            400: openapi.Response('Module déjà existant ou données manquantes'),
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        # gr_code = request.FILES.get("gr_code")
        reference_battery = request.data.get("reference_battery") or None
        reference_prise = request.data.get("reference_prise") or None
        reference_panneau = request.data.get("reference_panneau") or None
        activation_code = request.data.get("activation_code") or None
        active = request.data.get("active")
        user = request.data.get("user")

        if not user:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

        if Modules.objects.filter(user__id=user).exists():
            return Response(
                {"error": "module already existe"}, status=status.HTTP_400_BAD_REQUEST
            )

        #  user
        user_value = get_object_or_404(ProfilUser, id=user)

        # create user
        module = Modules.objects.create(
            user=user_value,
            reference_battery=reference_battery,
            reference_prise=reference_prise,
            reference_panneau=reference_panneau,
            activation_code=activation_code,
        )

        active_value = parse_boolean(active)
        if active_value is not None:
            module.active = active_value
            module.save(update_fields=["active"])

        #  gr_code
        # if gr_code:
        #     module.gr_code = gr_code
        #     module.save()

        serializer = ModulesSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Récupère un module par son ID",
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                description="Identifiant unique du module",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ModulesSerializer,
            404: openapi.Response('Module non trouvé'),
            500: 'Internal Server Error'
        }
    )
    def get(self, request, module_id):
        module = self.get_object(module_id=module_id)
        serializer = ModulesSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Met à jour un module par son ID",
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                description="Identifiant unique du module",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reference_battery': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée à la batterie du module', nullable=True),
                'reference_prise': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée à la prise du module', nullable=True),
                'reference_panneau': openapi.Schema(type=openapi.TYPE_STRING, description='Référence associée au panneau du module', nullable=True),
                'activation_code': openapi.Schema(type=openapi.TYPE_STRING, description="Code d'activation du module", nullable=True),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='ID de l\'utilisateur'),
                'active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Statut actif du module')
            }
        ),
        responses={
            200: ModulesSerializer,
            404: openapi.Response('Module non trouvé'),
            500: 'Internal Server Error'
        }
    )
    def put(self, request, module_id):
        module = self.get_object(module_id=module_id)
        # variables
        # gr_code = request.FILES.get("gr_code")
        reference_battery = request.data.get("reference_battery")
        reference_prise = request.data.get("reference_prise")
        reference_panneau = request.data.get("reference_panneau")
        activation_code = request.data.get("activation_code")
        user = request.data.get("user")
        active = request.data.get("active")

        #  gr_code
        # if gr_code:
        #     module.gr_code = gr_code
        #     module.save()

        if reference_battery is not None:
            module.reference_battery = reference_battery or None

        if reference_prise is not None:
            module.reference_prise = reference_prise or None

        if reference_panneau is not None:
            module.reference_panneau = reference_panneau or None

        if activation_code is not None:
            module.activation_code = activation_code or None

        #  active status
        active_value = parse_boolean(active)
        if active_value is not None:
            module.active = active_value

        #  user
        if user is not None:
            if user == "":
                module.user = None
            else:
                user_value = get_object_or_404(ProfilUser, id=user)
                module.user = user_value

        module.save()

        serializer = ModulesSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Supprime un module par son ID",
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                description="Identifiant unique du module",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: 'Module supprimé avec succès',
            404: openapi.Response('Module non trouvé'),
            500: 'Internal Server Error'
        }
    )
    def delete(self, request, module_id):
        module = self.get_object(module_id=module_id)
        module.delete()
        return Response(
            {"message": "module is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# Toggle module active status
@swagger_auto_schema(
    method='put',
    operation_description="Bascule le statut actif/inactif d'un module",
    manual_parameters=[
        openapi.Parameter(
            'module_id',
            openapi.IN_PATH,
            description="Identifiant unique du module",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Statut basculé avec succès'),
        404: openapi.Response('Module non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["PUT"])
def toggle_module_active(request, module_id):
    """
    Bascule le statut actif/inactif d'un module
    """
    try:
        module = Modules.objects.get(id=module_id)

        # Basculer le statut active
        module.active = not module.active
        module.save()

        serializer = ModulesSerializer(module, many=False)
        return Response({
            "message": f"Module {'activé' if module.active else 'désactivé'} avec succès",
            "module": serializer.data
        }, status=status.HTTP_200_OK)

    except Modules.DoesNotExist:
        return Response(
            {"error": "Module non trouvé"},
            status=status.HTTP_404_NOT_FOUND,
        )


# Get module with all related elements (battery, panneau, prise)
@swagger_auto_schema(
    method='get',
    operation_description="Récupère un module avec tous ses éléments associés (batterie, panneau, prise)",
    manual_parameters=[
        openapi.Parameter(
            'module_id',
            openapi.IN_PATH,
            description="Identifiant unique du module",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Module avec éléments associés'),
        404: openapi.Response('Module non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
def get_module_with_elements(request, module_id):
    """
    Récupère un module avec tous ses éléments associés
    """
    try:
        module = Modules.objects.get(id=module_id)

        # Récupérer les éléments associés
        try:
            battery = Battery.objects.get(module_id=module_id)
            battery_data = {
                "id": battery.id,
                "marque": battery.marque,
                "puissance": battery.puissance,
                "voltage": battery.voltage,
                "module_id": battery.module_id,
                "createdAt": battery.createdAt,
                "updatedAt": battery.updatedAt,
            }
        except Battery.DoesNotExist:
            battery_data = None

        try:
            panneau = Panneau.objects.get(module_id=module_id)
            panneau_data = {
                "id": panneau.id,
                "marque": panneau.marque,
                "puissance": panneau.puissance,
                "voltage": panneau.voltage,
                "module_id": panneau.module_id,
                "createdAt": panneau.createdAt,
                "updatedAt": panneau.updatedAt,
            }
        except Panneau.DoesNotExist:
            panneau_data = None

        try:
            prise = Prise.objects.get(module_id=module_id)
            prise_data = {
                "id": prise.id,
                "name": prise.name,
                "voltage": prise.voltage,
                "module_id": prise.module_id,
                "createdAt": prise.createdAt,
                "updatedAt": prise.updatedAt,
            }
        except Prise.DoesNotExist:
            prise_data = None

        # Sérialiser le module
        module_serializer = ModulesSerializer(module, many=False)

        response_data = {
            "module": module_serializer.data,
            "battery": battery_data,
            "panneau": panneau_data,
            "prise": prise_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Modules.DoesNotExist:
        return Response(
            {"error": "Module non trouvé"},
            status=status.HTTP_404_NOT_FOUND,
        )


# get all ModulesInfo
@swagger_auto_schema(
    method='get',
    operation_description="Récupère les informations d'un module",
    manual_parameters=[
        openapi.Parameter(
            'module_id',
            openapi.IN_PATH,
            description="Identifiant unique du module",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: ModulesInfoSerializer,
        404: openapi.Response('Informations du module non trouvées'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_moduleinfo_by_module(request, module_id):
    modules_info = ModulesInfo.objects.get(module__id=module_id)
    serializer = ModulesInfoSerializer(modules_info, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ModulesInfo APIView
class ModulesInfoAPIView(APIView):

    def get_object(self, module_id):
        try:
            return ModulesInfo.objects.get(id=module_id)
        except ModulesInfo.DoesNotExist:
            return Response(
                {"error": "modules Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_description="Crée de nouvelles informations de module",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['module', 'name', 'description'],
            properties={
                'module': openapi.Schema(type=openapi.TYPE_STRING, description='ID du module'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nom des informations'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description des informations')
            }
        ),
        responses={
            201: ModulesInfoSerializer,
            400: openapi.Response('Données manquantes'),
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        module = request.data.get("module")
        name = request.data.get("name")
        description = request.data.get("description")
        if name is None or module is None or description is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get module
        module_data = get_object_or_404(Modules, id=module)

        module_info = ModulesInfo.objects.create(
            name=name,
            module=module_data,
            description=description,
        )
        # save into database
        module_info.save()
        serializer = ModulesInfoSerializer(module_info, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Récupère les informations d'un module par leur ID",
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                description="Identifiant unique des informations du module",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ModulesInfoSerializer,
            404: openapi.Response('Informations du module non trouvées'),
            500: 'Internal Server Error'
        }
    )
    def get(self, request, module_id):
        module = self.get_object(module_id=module_id)
        serializer = ModulesInfoSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Met à jour les informations d'un module par leur ID",
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                description="Identifiant unique des informations du module",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nom des informations'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description des informations')
            }
        ),
        responses={
            200: ModulesInfoSerializer,
            404: openapi.Response('Informations du module non trouvées'),
            500: 'Internal Server Error'
        }
    )
    def put(self, request, module_id):
        module = self.get_object(module_id=module_id)
        # variables
        name = request.data.get("name")
        description = request.data.get("description")

        #  gr_code
        if name:
            module.name = name
            module.save()

        #  description
        if description:
            module.description = description
            module.save()

        serializer = ModulesInfoSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Supprime les informations d'un module par leur ID",
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                description="Identifiant unique des informations du module",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: 'Informations du module supprimées avec succès',
            404: openapi.Response('Informations du module non trouvées'),
            500: 'Internal Server Error'
        }
    )
    def delete(self, request, module_id):
        module = self.get_object(module_id=module_id)
        module.delete()
        return Response(
            {"message": "module is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# get all ModulesDetail
@swagger_auto_schema(
    method='get',
    operation_description="Récupère les détails d'un module",
    manual_parameters=[
        openapi.Parameter(
            'module_id',
            openapi.IN_PATH,
            description="Identifiant unique des détails du module",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: ModulesDetailSerializer,
        404: openapi.Response('Détails du module non trouvés'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_moduledetail_by_module(request, module_id):
    modules_detail = ModulesDetail.objects.get(module_info__id=module_id)
    serializer = ModulesDetailSerializer(modules_detail, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ModulesDetail APIView
class ModulesDetailAPIView(APIView):

    def get_object(self, module_id):
        try:
            return ModulesDetail.objects.get(id=module_id)
        except ModulesDetail.DoesNotExist:
            return Response(
                {"error": "modules detail not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_description="Crée de nouveaux détails de module",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['module_info', 'value', 'description'],
            properties={
                'module_info': openapi.Schema(type=openapi.TYPE_STRING, description='ID des informations du module'),
                'value': openapi.Schema(type=openapi.TYPE_STRING, description='Valeur du détail'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description du détail')
            }
        ),
        responses={
            201: ModulesDetailSerializer,
            400: openapi.Response('Données manquantes'),
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        module_info = request.data.get("module_info")
        value = request.data.get("value")
        description = request.data.get("description")
        if value is None or module_info is None or description is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get module
        module_data = get_object_or_404(ModulesInfo, id=module_info)

        module_detail = ModulesInfo.objects.create(
            value=value,
            module_info=module_data,
            description=description,
        )
        # save into database
        module_detail.save()
        serializer = ModulesInfoSerializer(module_detail, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Récupère les détails d'un module par leur ID",
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                description="Identifiant unique des détails du module",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ModulesDetailSerializer,
            404: openapi.Response('Détails du module non trouvés'),
            500: 'Internal Server Error'
        }
    )
    def get(self, request, module_id):
        module = self.get_object(module_id=module_id)
        serializer = ModulesInfoSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Met à jour les détails d'un module par leur ID",
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                description="Identifiant unique des détails du module",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nom des détails'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description des détails')
            }
        ),
        responses={
            200: ModulesDetailSerializer,
            404: openapi.Response('Détails du module non trouvés'),
            500: 'Internal Server Error'
        }
    )
    def put(self, request, module_id):
        module = self.get_object(module_id=module_id)
        # variables
        name = request.data.get("name")
        description = request.data.get("description")

        #  gr_code
        if name:
            module.name = name
            module.save()

        #  description
        if description:
            module.description = description
            module.save()

        serializer = ModulesInfoSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Supprime les détails d'un module par leur ID",
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                description="Identifiant unique des détails du module",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: 'Détails du module supprimés avec succès',
            404: openapi.Response('Détails du module non trouvés'),
            500: 'Internal Server Error'
        }
    )
    def delete(self, request, module_id):
        module = self.get_object(module_id=module_id)
        module.delete()
        return Response(
            {"message": "module is deleted"}, status=status.HTTP_204_NO_CONTENT
        )

