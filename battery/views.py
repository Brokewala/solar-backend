from rest_framework import status,permissions
# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
# from datetime import timezone
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# utils
from users.utils import _calculate_target_date,_get_french_day_name

# django
from datetime import timedelta
from datetime import datetime
from django.db.models import Sum, F, Avg
from django.db.models.functions import Coalesce
from django.db.models.functions import ExtractYear
from django.db.models import Q
from django.db.models import FloatField
from django.db.models.functions import ExtractMonth
from django.db.models.functions import Cast
from django.db.models.functions import ExtractWeekDay, ExtractWeek
from calendar import monthrange

# models
from .models import Battery
from .models import BatteryData
from .models import BatteryPlanning
from .models import BatteryRelaiState
from .models import BatteryReference
from module.models import Modules

# serailizer
from .serializers import BatterySerializer
from .serializers import BatteryDataSerializer
from .serializers import BatteryPlanningSerializer
from .serializers import BatteryReferenceSerializer
from .serializers import BatteryRelaiStateSerializer
from .serializers import BatteryAllSerializer


@swagger_auto_schema(
    method='get',
    operation_description="Récupère toutes les batteries avec leurs données complètes",
    responses={
        200: BatteryAllSerializer(many=True),
        400: 'Bad Request',
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_battery(request):
    batttery = Battery.objects.all().order_by("-createdAt")
    serializer = BatteryAllSerializer(batttery, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Récupère une batterie spécifique par l'ID du module",
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
        200: BatterySerializer,
        404: openapi.Response('Batterie non trouvée'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_battery_by_module(request, module_id):
    try:
        battery = Battery.objects.get(module__id=module_id)
        serializer = BatterySerializer(battery, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Battery.DoesNotExist:
        return Response(
            {"error": "battery not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

@swagger_auto_schema(
    method='put',
    operation_description="Met à jour les informations d'une batterie par l'ID du module",
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
            'puissance': openapi.Schema(type=openapi.TYPE_STRING, description='Puissance de la batterie (en W ou kW)'),
            'voltage': openapi.Schema(type=openapi.TYPE_STRING, description='Tension de la batterie (en V)'),
            'marque': openapi.Schema(type=openapi.TYPE_STRING, description='Marque du fabricant')
        }
    ),
    responses={
        200: BatterySerializer,
        404: openapi.Response('Batterie non trouvée'),
        500: 'Internal Server Error'
    }
)
@api_view(["PUT"])
# @permission_classes([IsAuthenticated])
def put_battery_by_module(request, module_id):
    try:
        battery = Battery.objects.get(module__id=module_id)
        # variables
        puissance = request.data.get("puissance")
        voltage = request.data.get("voltage")
        marque = request.data.get("marque")
        #  puissance
        if puissance:
            battery.puissance = puissance
            battery.save()

        #  voltage
        if voltage:
            battery.voltage = voltage
            battery.save()

        #  marque
        if marque:
            battery.marque = marque
            battery.save()

        serializer = BatterySerializer(battery, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Battery.DoesNotExist:
        return Response(
            {"error": "battery not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

# Battery APIView
class BatteryAPIView(APIView):

    def get_object(self, battery_id):
        try:
            return Battery.objects.get(id=battery_id)
        except Battery.DoesNotExist:
            return Response(
                {"error": "panneau not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_description="Crée une nouvelle batterie",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['puissance', 'voltage', 'module', 'marque'],
            properties={
                'puissance': openapi.Schema(type=openapi.TYPE_STRING, description='Puissance de la batterie (en W ou kW)'),
                'voltage': openapi.Schema(type=openapi.TYPE_STRING, description='Tension de la batterie (en V)'),
                'module': openapi.Schema(type=openapi.TYPE_STRING, description='ID du module associé'),
                'marque': openapi.Schema(type=openapi.TYPE_STRING, description='Marque du fabricant')
            }
        ),
        responses={
            201: BatterySerializer,
            400: openapi.Response('Données manquantes ou batterie déjà existante'),
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        puissance = request.data.get("puissance")
        voltage = request.data.get("voltage")
        module = request.data.get("module")
        marque = request.data.get("marque")

        if module is None or marque is None or puissance is None or voltage is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

         # module
        if Battery.objects.filter(module__id=module).exists():
            return Response(
                {"error": "batterie already existe"}, status=status.HTTP_400_BAD_REQUEST
            )

        # get module
        module_data = get_object_or_404(Modules, id=module)

        # create user
        battery = Battery.objects.create(
            puissance=puissance,
            voltage=voltage,
            module=module_data,
            marque=marque,
        )
        # save into database
        battery.save()

        serializer = BatterySerializer(battery, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Récupère une batterie par son ID",
        manual_parameters=[
            openapi.Parameter(
                'battery_id',
                openapi.IN_PATH,
                description="Identifiant unique de la batterie",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: BatterySerializer,
            404: openapi.Response('Batterie non trouvée'),
            500: 'Internal Server Error'
        }
    )
    def get(self, request, battery_id):
        battery = self.get_object(battery_id)
        serializer = BatterySerializer(battery, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Met à jour une batterie par son ID",
        manual_parameters=[
            openapi.Parameter(
                'battery_id',
                openapi.IN_PATH,
                description="Identifiant unique de la batterie",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'puissance': openapi.Schema(type=openapi.TYPE_STRING, description='Puissance de la batterie (en W ou kW)'),
                'voltage': openapi.Schema(type=openapi.TYPE_STRING, description='Tension de la batterie (en V)'),
                'marque': openapi.Schema(type=openapi.TYPE_STRING, description='Marque du fabricant')
            }
        ),
        responses={
            200: BatterySerializer,
            404: openapi.Response('Batterie non trouvée'),
            500: 'Internal Server Error'
        }
    )
    def put(self, request, battery_id):
        battery = self.get_object(battery_id)
        # variables
        puissance = request.data.get("puissance")
        voltage = request.data.get("voltage")
        marque = request.data.get("marque")

        #  puissance
        if puissance:
            battery.puissance = puissance
            battery.save()

        #  voltage
        if voltage:
            battery.voltage = voltage
            battery.save()

        #  marque
        if marque:
            battery.marque = marque
            battery.save()

        serializer = BatterySerializer(battery, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Supprime une batterie par son ID",
        manual_parameters=[
            openapi.Parameter(
                'battery_id',
                openapi.IN_PATH,
                description="Identifiant unique de la batterie",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: 'Batterie supprimée avec succès',
            404: openapi.Response('Batterie non trouvée'),
            500: 'Internal Server Error'
        }
    )
    def delete(self, request, battery_id):
        battery = self.get_object(battery_id)
        battery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# get all BatteryData
@swagger_auto_schema(
    method='get',
    operation_description="Récupère toutes les données d'une batterie spécifique",
    manual_parameters=[
        openapi.Parameter(
            'battery_id',
            openapi.IN_PATH,
            description="Identifiant unique de la batterie",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: BatteryDataSerializer(many=True),
        400: 'Bad Request',
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_batterydata_by_battery(request, battery_id):
    battery_data = BatteryData.objects.filter(battery__id=battery_id)
    serializer = BatteryDataSerializer(battery_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#  BatteryData APIView
class BatteryDataAPIView(APIView):

    def get_object(self, battery_data_id):
        try:
            return BatteryData.objects.get(id=battery_data_id)
        except BatteryData.DoesNotExist:
            return Response(
                {"error": "modules Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_description="Crée de nouvelles données de batterie",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['battery', 'tension', 'puissance', 'courant', 'energy', 'pourcentage'],
            properties={
                'battery': openapi.Schema(type=openapi.TYPE_STRING, description='ID de la batterie'),
                'tension': openapi.Schema(type=openapi.TYPE_STRING, description='Tension actuelle (en V)'),
                'puissance': openapi.Schema(type=openapi.TYPE_STRING, description='Puissance actuelle (en W)'),
                'courant': openapi.Schema(type=openapi.TYPE_STRING, description='Courant actuel (en A)'),
                'energy': openapi.Schema(type=openapi.TYPE_STRING, description='Énergie stockée (en Wh)'),
                'pourcentage': openapi.Schema(type=openapi.TYPE_STRING, description='Pourcentage de charge (%)')
            }
        ),
        responses={
            201: BatteryDataSerializer,
            400: openapi.Response('Données manquantes'),
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        tension = request.data.get("tension")
        puissance = request.data.get("puissance")
        courant = request.data.get("courant")
        energy = request.data.get("energy")
        pourcentage = request.data.get("pourcentage")
        battery = request.data.get("battery")

        if (
            tension is None
            or puissance is None
            or courant is None
            or energy is None
            or pourcentage is None
            or battery is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

        # get battery
        battery_data = get_object_or_404(Battery, id=battery)

        # create battery data
        battery_data_obj = BatteryData.objects.create(
            tension=tension,
            puissance=puissance,
            courant=courant,
            energy=energy,
            pourcentage=pourcentage,
            battery=battery_data,
        )
        # save into database
        battery_data_obj.save()

        serializer = BatteryDataSerializer(battery_data_obj, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Récupère des données de batterie par leur ID",
        manual_parameters=[
            openapi.Parameter(
                'battery_data_id',
                openapi.IN_PATH,
                description="Identifiant unique des données de batterie",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: BatteryDataSerializer,
            404: openapi.Response('Données de batterie non trouvées'),
            500: 'Internal Server Error'
        }
    )
    def get(self, request, battery_data_id):
        battery_data = self.get_object(battery_data_id)
        serializer = BatteryDataSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Met à jour des données de batterie par leur ID",
        manual_parameters=[
            openapi.Parameter(
                'battery_data_id',
                openapi.IN_PATH,
                description="Identifiant unique des données de batterie",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'tension': openapi.Schema(type=openapi.TYPE_STRING, description='Tension actuelle (en V)'),
                'puissance': openapi.Schema(type=openapi.TYPE_STRING, description='Puissance actuelle (en W)'),
                'courant': openapi.Schema(type=openapi.TYPE_STRING, description='Courant actuel (en A)'),
                'energy': openapi.Schema(type=openapi.TYPE_STRING, description='Énergie stockée (en Wh)'),
                'pourcentage': openapi.Schema(type=openapi.TYPE_STRING, description='Pourcentage de charge (%)')
            }
        ),
        responses={
            200: BatteryDataSerializer,
            404: openapi.Response('Données de batterie non trouvées'),
            500: 'Internal Server Error'
        }
    )
    def put(self, request, battery_data_id):
        battery_data = self.get_object(battery_data_id)
        # variables
        tension = request.data.get("tension")
        puissance = request.data.get("puissance")
        courant = request.data.get("courant")
        energy = request.data.get("energy")
        pourcentage = request.data.get("pourcentage")

        #  tension
        if tension:
            battery_data.tension = tension
            battery_data.save()

        #  puissance
        if puissance:
            battery_data.puissance = puissance
            battery_data.save()

        #  courant
        if courant:
            battery_data.courant = courant
            battery_data.save()

        #  energy
        if energy:
            battery_data.energy = energy
            battery_data.save()

        #  pourcentage
        if pourcentage:
            battery_data.pourcentage = pourcentage
            battery_data.save()

        serializer = BatteryDataSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Supprime des données de batterie par leur ID",
        manual_parameters=[
            openapi.Parameter(
                'battery_data_id',
                openapi.IN_PATH,
                description="Identifiant unique des données de batterie",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: 'Données de batterie supprimées avec succès',
            404: openapi.Response('Données de batterie non trouvées'),
            500: 'Internal Server Error'
        }
    )
    def delete(self, request, battery_data_id):
        battery_data = self.get_object(battery_data_id)
        battery_data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# get all BatteryPlanning
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_batteryplanning_by_battery(request, battery_id):
    battery_data = BatteryPlanning.objects.filter(battery__id=battery_id)
    serializer = BatteryPlanningSerializer(battery_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# plannig by module
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_BatteryPlanning_by_module(request, module_id):
    module_data = get_object_or_404(Modules, id=module_id)
    battery_value = get_object_or_404(Battery, module=module_data.id)
    battery_data = BatteryPlanning.objects.filter(battery__id=battery_value.id)
    serializer = BatteryPlanningSerializer(battery_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#  BatteryPlanning APIView
class BatteryPlanningPIView(APIView):

    def get_object(self, battery_planning_id):
        try:
            return BatteryPlanning.objects.get(id=battery_planning_id)
        except BatteryPlanning.DoesNotExist:
            return Response(
                {"error": "battery planning Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        energie = request.data.get("energie")
        date_debut = request.data.get("date_debut")
        date_fin = request.data.get("date_fin")
        done = request.data.get("done")
        battery_id = request.data.get("battery_id")
        date_value = request.data.get("date_value")

        if (
            energie is None
            or date_debut is None
            or date_fin is None
            or done is None
            or battery_id is None
            or date_value is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get battery
        battery = get_object_or_404(Battery, id=battery_id)

        battery_data = BatteryPlanning.objects.create(
            energie=energie,
            battery=battery,
            date_debut=date_debut,
            date_fin=date_fin,
            date=date_value,
            done=done,
        )
        # save into database
        battery_data.save()
        serializer = BatteryPlanningSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, battery_planning_id):
        module = self.get_object(battery_planning_id=battery_planning_id)
        serializer = BatteryPlanningSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, battery_planning_id):
        battery_data = self.get_object(battery_planning_id=battery_planning_id)
        # variables
        energie = request.data.get("energie")
        date_debut = request.data.get("date_debut")
        date_fin = request.data.get("date_fin")
        done = request.data.get("done")
        date = request.data.get("date")

        #  energie
        if energie:
            battery_data.energie = energie
            battery_data.save()

        #  date_debut
        if date_debut:
            battery_data.date_debut = date_debut
            battery_data.save()

        #  date_fin
        if date_fin:
            battery_data.date_fin = date_fin
            battery_data.save()

        #  done
        if done:
            battery_data.done = done
            battery_data.save()

        #  date
        if date:
            battery_data.date = date
            battery_data.save()

        serializer = BatteryPlanningSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, battery_planning_id):
        battery = self.get_object(battery_planning_id=battery_planning_id)
        battery.delete()
        return Response(
            {"message": "battery planning is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


# BatteryRelaiState BatteryRelaiStateSerializer
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_batteryrelaistate_by_battery(request, battery_id):
    battery_data = BatteryRelaiState.objects.filter(battery__id=battery_id).first()
    serializer = BatteryRelaiStateSerializer(battery_data, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def switch_batteryRelaiState_by_battery(request, battery_id):
    if not battery_id:
        return Response(
            {"detail": "battery ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if the battery exists
    battery_value = get_object_or_404(Battery, id=battery_id)
    relai_state = get_object_or_404(BatteryRelaiState, battery=battery_value)


    # Toggle the state and associated attributes
    if relai_state.active:
        # Set to inactive state
        relai_state.active = False
        relai_state.state = "low"
        relai_state.couleur = "red"
        relai_state.valeur = "0"
    else:
        # Set to active state
        relai_state.active = True
        relai_state.state = "high"
        relai_state.couleur = "green"
        relai_state.valeur = "1"

    # Save the updated state
    relai_state.save()
    serializer = BatteryRelaiStateSerializer(relai_state, many=False)

    # Return the new state
    return Response(serializer.data,
        status=status.HTTP_200_OK,
    )



#  BatteryRelaiState APIView
class BatteryRelaiStateAPIView(APIView):

    def get_object(self, battery_relai_id):
        try:
            return BatteryRelaiState.objects.get(id=battery_relai_id)
        except BatteryRelaiState.DoesNotExist:
            return Response(
                {"error": " Battery Relai State Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        active = request.data.get("active")
        state = request.data.get("state")
        couleur = request.data.get("couleur")
        valeur = request.data.get("valeur")
        battery_id = request.data.get("battery_id")

        if (
            active is None
            or state is None
            or couleur is None
            or valeur is None
            or battery_id is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get battery
        battery = get_object_or_404(Battery, id=battery_id)

        battery_data = BatteryRelaiState.objects.create(
            active=active,
            battery=battery,
            state=state,
            couleur=couleur,
            valeur=valeur,
        )
        # save into database
        battery_data.save()
        serializer = BatteryRelaiStateSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, battery_relai_id):
        battery_data = self.get_object(battery_relai_id=battery_relai_id)
        serializer = BatteryRelaiStateSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, battery_relai_id):
        battery_data = self.get_object(battery_relai_id=battery_relai_id)
        # variables
        active = request.data.get("active")
        state = request.data.get("state")
        couleur = request.data.get("couleur")
        valeur = request.data.get("valeur")

        #  active
        if active:
            battery_data.active = active
            battery_data.save()

        #  state
        if state:
            battery_data.state = state
            battery_data.save()

        #  couleur
        if couleur:
            battery_data.couleur = couleur
            battery_data.save()

        #  valeur
        if valeur:
            battery_data.valeur = valeur
            battery_data.save()

        serializer = BatteryRelaiStateSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, battery_relai_id):
        battery = self.get_object(battery_relai_id=battery_relai_id)
        battery.delete()
        return Response(
            {"message": "battery planning is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


class BatteryRelaiStateByBatteryAPIView(APIView):
    """
    GET  /battery/<battery_id>/relai-state/  -> retourne l'état du relais de la batterie
    PUT  /battery/<battery_id>/relai-state/  -> met à jour l'état du relais de la batterie
    """
    permission_classes = [permissions.IsAuthenticated]  # retire si endpoint public

    def get_object(self, battery_id: str) -> BatteryRelaiState:
        # Sécurise : 404 si la batterie n'existe pas
        get_object_or_404(Battery, id=battery_id)
        # Récupère l'état du relais lié à cette batterie
        return get_object_or_404(BatteryRelaiState, battery__id=battery_id)

    def get(self, request, battery_id: str):
        relai_state = self.get_object(battery_id)
        serializer = BatteryRelaiStateSerializer(relai_state)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, battery_id: str):
        relai_state = self.get_object(battery_id)
        # partial=True pour permettre de ne mettre que certains champs
        serializer = BatteryRelaiStateSerializer(relai_state, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # garde le même relai_state (pas de swap de battery)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# BatteryReference  BatteryReferenceSerializer
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_batteryreference_by_battery(request, battery_id):
    battery_data = BatteryReference.objects.filter(battery__id=battery_id)
    serializer = BatteryReferenceSerializer(battery_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class BatteryReferenceAPIView(APIView):

    def get_object(self, battery_reference_id):
        try:
            return BatteryReference.objects.get(id=battery_reference_id)
        except BatteryReference.DoesNotExist:
            return Response(
                {"error": " Battery reference Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        checked_data = request.data.get("checked_data")
        checked_state = request.data.get("checked_state")
        duration = request.data.get("duration")
        energy = request.data.get("energy")
        battery_id = request.data.get("battery_id")

        if (
            checked_data is None
            or checked_state is None
            or duration is None
            or energy is None
            or battery_id is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get battery
        battery = get_object_or_404(Battery, id=battery_id)

        battery_data = BatteryReference.objects.create(
            checked_data=checked_data,
            battery=battery,
            checked_state=checked_state,
            duration=duration,
            energy=energy,
        )
        # save into database
        battery_data.save()
        serializer = BatteryReferenceSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, battery_reference_id):
        battery_data = self.get_object(battery_reference_id=battery_reference_id)
        serializer = BatteryReferenceSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, battery_reference_id):
        battery_data = self.get_object(battery_reference_id=battery_reference_id)
        # variables
        checked_data = request.data.get("checked_data")
        checked_state = request.data.get("checked_state")
        duration = request.data.get("duration")
        energy = request.data.get("energy")

        #  energie
        if checked_data:
            battery_data.checked_data = checked_data
            battery_data.save()

        #  checked_state
        if checked_state:
            battery_data.checked_state = checked_state
            battery_data.save()

        #  duration
        if duration:
            battery_data.duration = duration
            battery_data.save()

        #  energy
        if energy:
            battery_data.energy = energy
            battery_data.save()

        serializer = BatteryReferenceSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, battery_reference_id):
        battery = self.get_object(battery_reference_id=battery_reference_id)
        battery.delete()
        return Response(
            {"message": "battery reference is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )

# auto
@receiver(post_save, sender=Battery)
def create_relai_state_auto_battery(sender, instance, created, **kwargs):
    if created:
        # create
        relay=BatteryRelaiState.objects.create(
            battery= instance,
            active= False,
            state= "low",
            couleur= "green",
            valeur="0"
        )
        relay.save()

# =============================app mobile=====================================
# getDureeUtilisationbatteryAnuelleByIdModule
@api_view(["GET"])
def get_duree_utilisation_batterie_annuelle_by_id_module(request, module_id):
    try:
        # Vérifier si le module existe
        module = Modules.objects.get(id=module_id)

        # Récupérer l'année en cours
        current_year = datetime.now().year

        # Récupérer les BatteryPlanning associés au module pour l'année en cours
        plannings = BatteryPlanning.objects.filter(
            battery__module=module,
            date__year=current_year,
        )

        # Calculer la durée totale d'utilisation en heures
        total_duration = 0
        for planning in plannings:
            if planning.date_debut and planning.date_fin:
                # Calculer la durée entre date_debut et date_fin
                duration = (
                    datetime.combine(datetime.min, planning.date_fin) -
                    datetime.combine(datetime.min, planning.date_debut)
                ).total_seconds() / 3600  # Conversion en heures
                total_duration += max(duration, 0)  # Éviter les valeurs négatives

        return Response(
            {"duree_annuelle": round(total_duration, 2)},  # Arrondi à 2 décimales
            status=status.HTTP_200_OK,
        )

    except Modules.DoesNotExist:
        return Response(
            {"error": "Le module avec l'ID spécifié n'existe pas."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@api_view(["GET"])
def yearly_battery_utilisation(request, module_id):
    try:
        module = get_object_or_404(Modules, id=module_id)
        battery = get_object_or_404(Battery, module=module)
        # Vérifier si des données existent pour la batterie spécifiée
        current_year = datetime.now().year

        # Récupérer et regrouper les données par mois
        monthly_data = (
            BatteryData.objects.filter(battery=battery, createdAt__year=current_year)
            .annotate(month=ExtractMonth("createdAt"))  # Extraire le mois de la date
            .values("month")
            .annotate(
                total_energy=Sum(Cast("energy", FloatField())),  # Somme de l'énergie par mois
                total_voltage=Sum(Cast("tension", FloatField())),  # Somme de la tension par mois
                total_current=Sum(Cast("courant", FloatField())),  # Somme du courant par mois
            )
            .order_by("month")
        )

        # Préparer les données au format requis
        response_data = {
            "labels": [data['month'] for data in monthly_data],
            "data": [data["total_energy"] for data in monthly_data],
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except BatteryData.DoesNotExist:
        return Response(
            {"error": "Aucune donnée trouvée pour la batterie spécifiée."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# getCouleurbatteryByIdModule
@api_view(["GET"])
def get_couleur_batterie_by_id_module(request, module_id):
    """
    Endpoint DRF pour obtenir les couleurs des batterys associées à un module spécifique.

    :param request: Objet de requête
    :param module_id: ID du module (passé dans l'URL)
    :return: JSON contenant les couleurs des batterys ou un message d'erreur
    """
    try:
        # Vérifier si le module existe
        module = Modules.objects.get(id=module_id)


        # Extraire les couleurs via BatteryRelaiState
        relai_state = BatteryRelaiState.objects.filter(battery__module=module).first()
        serialzier =BatteryRelaiStateSerializer(relai_state)
        return Response(serialzier.data, status=status.HTTP_200_OK)

    except Modules.DoesNotExist:
        return Response(
            {"error": "Le module avec l'ID spécifié n'existe pas."},
            status=status.HTTP_404_NOT_FOUND,
        )

    except Exception as e:
        return Response(
            {"error": "Une erreur s'est produite.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# listebatteryDataByDateAndIdModule
@api_view(["GET"])
def liste_batterie_data_by_date_and_id_module(request, module_id,date):

    # Validation des paramètres de date
    if not date :
        return Response(
            {"error": "Les paramètres 'start_date' et 'end_date' sont requis."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Vérification de l'existence du module
        module = Modules.objects.get(id=module_id)

        # Conversion des dates en objets datetime
        start_date_obj = datetime.strptime(date, "%Y-%m-%d")
        # end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

        # Récupérer les batterys associées au module
        batterys = module.modules_battery.all()

        # Filtrer les BatteryData par batterys et plage de dates
        battery_data = BatteryData.objects.filter(
            battery__in=batterys,
            createdAt__range=(start_date_obj)
        )

        # Serializer les données
        serialized_data = BatteryDataSerializer(battery_data, many=True).data

        return Response(serialized_data, status=status.HTTP_200_OK)

    except Modules.DoesNotExist:
        return Response(
            {"error": "Le module avec l'ID spécifié n'existe pas."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ValueError as e:
        return Response(
            {"error": f"Erreur dans le format des dates : {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# listeDureebatteryMensuelleByIdModuleAndMonth
@api_view(["GET"])
def liste_duree_batterie_mensuelle_by_id_module_and_month(request, module_id):

    today = datetime.today()
    current_year = today.year
    current_month = today.month

    # Déterminer les premiers et derniers jours du mois
    _, last_day_of_month = monthrange(current_year, current_month)
    start_of_month = datetime(current_year, current_month, 1)
    end_of_month = datetime(current_year, current_month, last_day_of_month)

    # Récupérer les données agrégées par semaine
    #Sum(Cast("energy", FloatField()))
    data = (
        BatteryData.objects.filter(
            battery__module_id=module_id,
            createdAt__gte=start_of_month,
            createdAt__lte=end_of_month,
        )
        .annotate(week=ExtractWeek("createdAt"))
        .values("week")
        .annotate(total_consumption=Sum(Cast("energy", FloatField())))
        .order_by("week")
    )

    # Générer les labels pour chaque semaine du mois
    start_of_week = start_of_month
    weekly_labels = []
    while start_of_week <= end_of_month:
        end_of_week = min(start_of_week + timedelta(days=6), end_of_month)
        weekly_labels.append(
            f"Semaine du {start_of_week.strftime('%d %b')} au {end_of_week.strftime('%d %b')}"
        )
        start_of_week += timedelta(days=7)

    # Mapper les données agrégées par semaine
    consumption_data = [0] * len(weekly_labels)

    for entry in data:
        week_number = entry["week"]
        week_index = week_number - start_of_month.isocalendar()[1]
        if 0 <= week_index < len(consumption_data):
            consumption_data[week_index] = entry["total_consumption"]

    return Response({"labels": weekly_labels, "data": consumption_data})

@api_view(["GET"])
def get_battery_consumption_by_week(request,module_id):
    """
    Retrieve battery consumption for each day of the current week, aggregated by day.
    """
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi de cette semaine
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche de cette semaine

    # Récupérer les données et extraire le jour de la semaine
    # Cast("energy", FloatField())
    data = (
        BatteryData.objects.filter(
            battery__module_id=module_id,
            createdAt__gte=start_of_week,
            createdAt__lte=end_of_week,
        )
        .annotate(day_of_week=ExtractWeekDay("createdAt"))
        .values("day_of_week")
        .annotate(total_consumption=Sum(Cast("energy", FloatField())))
        .order_by("day_of_week")
    )

    # Mapper les jours de la semaine (1 = Dimanche, 2 = Lundi, ..., 7 = Samedi)
    week_labels = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    consumption_data = {label: 0 for label in week_labels}

    for entry in data:
        day_of_week = entry["day_of_week"]
        consumption_data[week_labels[day_of_week - 1]] = entry["total_consumption"]

    # Préparer les labels et les data
    labels = list(consumption_data.keys())
    data = list(consumption_data.values())

    return Response({"labels": labels, "data": data})


@api_view(["GET"])
def get_weekly_battery_data_for_month(request, module_id, year, month):
    """
    Retrieve battery consumption for each week of a given month, aggregated by day of the week.
    """
    try:
        # Convertir year et month en entiers
        year = int(year)
        month = int(month)
    except ValueError:
        return Response({"error": "Year and month must be integers."}, status=400)

    # Vérifier que le mois est valide
    if not (1 <= month <= 12):
        return Response({"error": "Month must be between 1 and 12."}, status=400)

    # Déterminer les premiers et derniers jours du mois
    _, last_day_of_month = monthrange(year, month)
    start_of_month = datetime(year, month, 1)
    end_of_month = datetime(year, month, last_day_of_month, 23, 59, 59)

    # Vérifier les dates de la plage
    print(f"Plage de dates : {start_of_month} à {end_of_month}")

    # Récupérer les données de la base de données
    data = (
        BatteryData.objects.filter(
            battery__module_id=module_id,
            createdAt__gte=start_of_month,
            createdAt__lte=end_of_month,
        )
        .annotate(
            week=ExtractWeek("createdAt"),
            day_of_week=ExtractWeekDay("createdAt")
        )
        .values("week", "day_of_week")
        .annotate(total_consumption=Sum(Cast("energy", FloatField())))
        .order_by("week", "day_of_week")
    )

    # print(f"Données récupérées : {data}")  # Debug des données brutes

    # Mapper les jours de la semaine (1 = Dimanche, ..., 7 = Samedi)
    week_labels = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

    # Organisation des données par semaine
    weekly_data = {}
    for entry in data:
        week_number = entry["week"]
        day_of_week = entry["day_of_week"]
        total_consumption = entry["total_consumption"]

        # Initialiser les données pour la semaine si nécessaire
        if week_number not in weekly_data:
            weekly_data[week_number] = {"labels": week_labels, "data": [0] * 7}

        # Ajouter la consommation totale pour le jour de la semaine
        weekly_data[week_number]["data"][day_of_week - 1] = total_consumption

    # Créer une réponse organisée par semaine
    response_data = []
    for week_number in sorted(weekly_data.keys()):
        response_data.append({
            "week": f"Semaine {week_number}",
            "labels": weekly_data[week_number]["labels"],
            "data": weekly_data[week_number]["data"]
        })

    # Ajouter les semaines sans données
    current_date = start_of_month
    while current_date <= end_of_month:
        week_number = current_date.isocalendar()[1]  # Récupérer la semaine ISO
        if week_number not in weekly_data:
            response_data.append({
                "week": f"Semaine {week_number}",
                "labels": week_labels,
                "data": [0] * 7
            })
        current_date += timedelta(weeks=1)

    return Response(response_data)


# @api_view(["GET"])
# def get_daily_battery_data_for_week(request, module_id, week_number, day_of_week):
#     """
#     Retrieve battery data for a specific day (e.g., Saturday) of a given week number.
#     The response will return hours as labels and corresponding data for fields like
#     tension, puissance, courant, energy, and pourcentage.
#     """
#     try:
#         week_number = int(week_number)  # Conversion en entier
#     except ValueError:
#         return Response({"error": "week_number must be an integer."}, status=400)

#     # Traduction des jours de la semaine (français -> anglais)
#     french_to_english_days = {
#         "lundi": "Monday",
#         "mardi": "Tuesday",
#         "mercredi": "Wednesday",
#         "jeudi": "Thursday",
#         "vendredi": "Friday",
#         "samedi": "Saturday",
#         "dimanche": "Sunday",
#     }

#     # Traduire le jour en anglais
#     day_of_week = french_to_english_days.get(day_of_week.lower())
#     if not day_of_week:
#         return Response(
#             {"error": "Invalid day_of_week. Please provide a valid day in French."},
#             status=400,
#         )

#     # Calculer la date du premier jour de l'année
#     first_day_of_year = datetime(datetime.today().year, 1, 1)

#     # Ajuster pour commencer la semaine un lundi si ce n'est pas le cas
#     if first_day_of_year.weekday() != 0:  # 0 = lundi
#         first_day_of_year -= timedelta(days=first_day_of_year.weekday())

#     # Calculer la date du début de la semaine demandée
#     start_of_week = first_day_of_year + timedelta(weeks=week_number - 1)

#     # Trouver l'index du jour spécifié
#     days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#     day_of_week_index = days_of_week.index(day_of_week)

#     # Calculer la date cible
#     target_day = start_of_week + timedelta(days=day_of_week_index)

#     # Plage de temps pour inclure toutes les heures de la journée cible
#     start_of_day = datetime.combine(target_day, datetime.min.time()).replace(tzinfo=timezone.utc)
#     end_of_day = datetime.combine(target_day, datetime.max.time()).replace(tzinfo=timezone.utc)

#     # Filtrer les données de batterie pour cette plage horaire
#     data = (
#         BatteryData.objects.filter(
#             battery__module_id=module_id,
#             createdAt__range=(start_of_day, end_of_day),
#         )
#         .values("createdAt__hour")
#         .order_by("createdAt__hour")
#         # .annotate(
#         #     total_tension=Sum(Cast("tension", FloatField())),
#         #     total_puissance=Sum(Cast("puissance", FloatField())),
#         #     total_courant=Sum(Cast("courant", FloatField())),
#         #     total_energy=Sum(Cast("energy", FloatField())),
#         #     total_pourcentage=Sum(Cast("pourcentage", FloatField())),
#         # )
#     )

#     # Créer une liste des données horaires
#     result = []
#     for hour in range(24):
#         hour_data = next(
#             (
#                 {
#                     "hour": hour,
#                     "tension": entry["total_tension"] or 0,
#                     "puissance": entry["total_puissance"] or 0,
#                     "courant": entry["total_courant"] or 0,
#                     "energy": entry["total_energy"] or 0,
#                     "pourcentage": entry["total_pourcentage"] or 0,
#                 }
#                 for entry in data
#                 if entry["createdAt__hour"] == hour
#             ),
#             {
#                 "hour": hour,
#                 "tension": 0,
#                 "puissance": 0,
#                 "courant": 0,
#                 "energy": 0,
#                 "pourcentage": 0,
#             },
#         )
#         result.append(hour_data)

#     return Response(result)


@api_view(["GET"])
def get_daily_battery_data_for_week(request, module_id, week_number, day_of_week):
    """
    Retrieve real battery data for a specific day with exact timestamps.
    Returns all individual data points as inserted by users for accurate daily visualization.
    """
    try:
        week_number = int(week_number)
    except ValueError:
        return Response({"error": "week_number must be an integer."}, status=400)

    # Traduction des jours de la semaine (français -> anglais)
    french_to_english_days = {
        "lundi": "Monday",
        "mardi": "Tuesday",
        "mercredi": "Wednesday",
        "jeudi": "Thursday",
        "vendredi": "Friday",
        "samedi": "Saturday",
        "dimanche": "Sunday",
    }

    # Traduire le jour en anglais
    day_of_week = french_to_english_days.get(day_of_week.lower())
    if not day_of_week:
        return Response(
            {"error": "Invalid day_of_week. Please provide a valid day in French."},
            status=400,
        )

    # Calculer la date du premier jour de l'année
    first_day_of_year = datetime(datetime.today().year, 1, 1)

    # Ajuster pour commencer la semaine un lundi si ce n'est pas le cas
    if first_day_of_year.weekday() != 0:  # 0 = lundi
        first_day_of_year -= timedelta(days=first_day_of_year.weekday())

    # Calculer la date du début de la semaine demandée
    start_of_week = first_day_of_year + timedelta(weeks=week_number - 1)

    # Trouver l'index du jour spécifié
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week_index = days_of_week.index(day_of_week)

    # Calculer la date cible
    target_day = start_of_week + timedelta(days=day_of_week_index)

    # Plage de temps pour inclure toutes les heures de la journée cible
    start_of_day = datetime.combine(target_day, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(target_day, datetime.max.time()).replace(tzinfo=timezone.utc)

    # Récupérer toutes les données réelles de batterie pour cette journée
    battery_data = BatteryData.objects.filter(
        battery__module_id=module_id,
        createdAt__range=(start_of_day, end_of_day),
    ).order_by("createdAt").values(
        "createdAt", "tension", "puissance", "courant", "energy", "pourcentage"
    )

    # Convertir les données au format professionnel pour les graphiques
    result = []
    for entry in battery_data:
        created_at = entry["createdAt"]

        # Calculer l'heure décimale pour un affichage précis
        hour_decimal = created_at.hour + (created_at.minute / 60.0) + (created_at.second / 3600.0)

        # Formatage professionnel des données
        data_point = {
            "timestamp": created_at.isoformat(),
            "hour_decimal": round(hour_decimal, 3),
            "hour_label": created_at.strftime("%H:%M:%S"),
            "date_label": created_at.strftime("%d/%m/%Y"),
            "tension": float(entry["tension"]) if entry["tension"] else 0.0,
            "puissance": float(entry["puissance"]) if entry["puissance"] else 0.0,
            "courant": float(entry["courant"]) if entry["courant"] else 0.0,
            "energy": float(entry["energy"]) if entry["energy"] else 0.0,
            "pourcentage": float(entry["pourcentage"]) if entry["pourcentage"] else 0.0,
        }
        result.append(data_point)

    # Métadonnées professionnelles
    response_data = {
        "date": target_day.strftime("%Y-%m-%d"),
        "day_name": day_of_week,
        "week_number": week_number,
        "total_records": len(result),
        "data_range": {
            "start": start_of_day.isoformat(),
            "end": end_of_day.isoformat()
        },
        "data": result
    }

    return Response(response_data)


@api_view(["GET"])
def get_detailed_battery_data_for_week(request, module_id, week_number, day_of_week):
    """
    Retrieve detailed battery data for a specific day with real timestamps.
    Returns all individual data points with their exact timestamps for ImprovedDailyLine component.
    """
    try:
        week_number = int(week_number)
    except ValueError:
        return Response({"error": "week_number must be an integer."}, status=400)

    # Traduction des jours de la semaine (français -> anglais)
    french_to_english_days = {
        "lundi": "Monday",
        "mardi": "Tuesday",
        "mercredi": "Wednesday",
        "jeudi": "Thursday",
        "vendredi": "Friday",
        "samedi": "Saturday",
        "dimanche": "Sunday",
    }

    # Traduire le jour en anglais
    day_of_week = french_to_english_days.get(day_of_week.lower())
    if not day_of_week:
        return Response(
            {"error": "Invalid day_of_week. Please provide a valid day in French."},
            status=400,
        )

    # Calculer la date du premier jour de l'année
    first_day_of_year = datetime(datetime.today().year, 1, 1)

    # Ajuster pour commencer la semaine un lundi si ce n'est pas le cas
    if first_day_of_year.weekday() != 0:  # 0 = lundi
        first_day_of_year -= timedelta(days=first_day_of_year.weekday())

    # Calculer la date du début de la semaine demandée
    start_of_week = first_day_of_year + timedelta(weeks=week_number - 1)

    # Trouver l'index du jour spécifié
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week_index = days_of_week.index(day_of_week)

    # Calculer la date cible
    target_day = start_of_week + timedelta(days=day_of_week_index)

    # Plage de temps pour inclure toutes les heures de la journée cible
    start_of_day = datetime.combine(target_day, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(target_day, datetime.max.time()).replace(tzinfo=timezone.utc)

    # Récupérer toutes les données de batterie pour cette journée
    battery_data = BatteryData.objects.filter(
        battery__module_id=module_id,
        createdAt__range=(start_of_day, end_of_day),
    ).order_by("createdAt").values(
        "createdAt", "tension", "puissance", "courant", "energy", "pourcentage"
    )

    # Convertir les données au format souhaité
    result = []
    for entry in battery_data:
        # Convertir le timestamp en heure décimale (ex: 14.5 pour 14h30)
        created_at = entry["createdAt"]
        hour_decimal = created_at.hour + (created_at.minute / 60.0) + (created_at.second / 3600.0)

        result.append({
            "timestamp": created_at.isoformat(),
            "hour_decimal": round(hour_decimal, 2),
            "hour_label": f"{created_at.hour:02d}:{created_at.minute:02d}",
            "tension": float(entry["tension"]) if entry["tension"] else 0,
            "puissance": float(entry["puissance"]) if entry["puissance"] else 0,
            "courant": float(entry["courant"]) if entry["courant"] else 0,
            "energy": float(entry["energy"]) if entry["energy"] else 0,
            "pourcentage": float(entry["pourcentage"]) if entry["pourcentage"] else 0,
        })

    return Response(result)


@api_view(["GET"])
def get_current_battery_level(request, module_id):
    """
    Récupère le niveau de batterie actuel pour un module donné
    """
    try:
        # Vérifier si le module existe
        module = get_object_or_404(Modules, id=module_id)

        # Récupérer la batterie associée au module
        battery = get_object_or_404(Battery, module=module)

        # Récupérer la donnée la plus récente de la batterie
        latest_battery_data = BatteryData.objects.filter(
            battery=battery
        ).order_by('-createdAt').first()

        if not latest_battery_data:
            return Response({
                "level": 0,
                "status": "no_data",
                "message": "Aucune donnée de batterie disponible"
            }, status=status.HTTP_200_OK)

        # Calculer le niveau de batterie
        battery_level = float(latest_battery_data.pourcentage) if latest_battery_data.pourcentage else 0

        # Déterminer le statut basé sur le niveau
        if battery_level >= 80:
            battery_status = "excellent"
        elif battery_level >= 60:
            battery_status = "good"
        elif battery_level >= 40:
            battery_status = "medium"
        elif battery_level >= 20:
            battery_status = "low"
        else:
            battery_status = "critical"

        response_data = {
            "level": battery_level,
            "status": battery_status,
            "voltage": float(latest_battery_data.tension) if latest_battery_data.tension else 0,
            "current": float(latest_battery_data.courant) if latest_battery_data.courant else 0,
            "power": float(latest_battery_data.puissance) if latest_battery_data.puissance else 0,
            "energy": float(latest_battery_data.energy) if latest_battery_data.energy else 0,
            "last_update": latest_battery_data.createdAt.isoformat(),
            "battery_info": {
                "id": battery.id,
                "marque": battery.marque,
                "puissance": battery.puissance,
                "voltage": battery.voltage,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Modules.DoesNotExist:
        return Response({
            "error": "Module non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Battery.DoesNotExist:
        return Response({
            "error": "Aucune batterie associée à ce module"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            "error": "Erreur interne du serveur",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_monthly_production_summary(request, module_id):
    """
    Récupère un résumé de la production mensuelle pour tous les composants d'un module
    """
    try:
        # Vérifier si le module existe
        module = get_object_or_404(Modules, id=module_id)

        current_year = datetime.now().year
        current_month = datetime.now().month

        # Récupérer les données de production des panneaux
        from panneau.models import PanneauData
        panneau_production = PanneauData.objects.filter(
            panneau__module=module,
            createdAt__year=current_year,
            createdAt__month=current_month
        ).aggregate(
            total_production=Sum(Cast("energy", FloatField()))
        )

        # Récupérer les données de consommation des prises
        from prise.models import PriseData
        prise_consumption = PriseData.objects.filter(
            prise__module=module,
            createdAt__year=current_year,
            createdAt__month=current_month
        ).aggregate(
            total_consumption=Sum(Cast("energy", FloatField()))
        )

        # Récupérer les données de stockage des batteries
        battery_storage = BatteryData.objects.filter(
            battery__module=module,
            createdAt__year=current_year,
            createdAt__month=current_month
        ).aggregate(
            total_storage=Sum(Cast("energy", FloatField()))
        )

        # Calculer les totaux
        total_production = panneau_production.get('total_production', 0) or 0
        total_consumption = prise_consumption.get('total_consumption', 0) or 0
        total_storage = battery_storage.get('total_storage', 0) or 0

        # Calculer l'efficacité
        efficiency = 0
        if total_production > 0:
            efficiency = ((total_production - total_consumption) / total_production) * 100

        response_data = {
            "month": current_month,
            "year": current_year,
            "production": {
                "total": round(total_production, 2),
                "unit": "kWh",
                "source": "panneaux_solaires"
            },
            "consumption": {
                "total": round(total_consumption, 2),
                "unit": "kWh",
                "source": "prises"
            },
            "storage": {
                "total": round(total_storage, 2),
                "unit": "kWh",
                "source": "batteries"
            },
            "balance": {
                "net": round(total_production - total_consumption, 2),
                "efficiency": round(efficiency, 1),
                "unit": "kWh"
            },
            "module_info": {
                "id": module.id,
                "name": getattr(module, 'name', 'Module'),
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Modules.DoesNotExist:
        return Response({
            "error": "Module non trouvé"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            "error": "Erreur interne du serveur",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_battery_relay_state_by_module(request, module_id):
    """
    Récupère l'état du relais de la batterie pour un module donné
    """
    try:
        # Vérifier si le module existe
        module = get_object_or_404(Modules, id=module_id)

        # Récupérer la batterie associée au module
        battery = Battery.objects.filter(module=module).first()

        if not battery:
            return Response({
                "couleur": "gray",
                "active": False,
                "message": "Aucune batterie trouvée pour ce module"
            }, status=status.HTTP_200_OK)

        # Récupérer l'état du relais de la batterie
        relay_state = BatteryRelaiState.objects.filter(battery=battery).first()

        if not relay_state:
            # Créer un état par défaut si aucun n'existe
            relay_state = BatteryRelaiState.objects.create(
                battery=battery,
                active=False,
                state="low",
                couleur="red",
                valeur="0"
            )

        return Response({
            "couleur": relay_state.couleur,
            "active": relay_state.active,
            "state": relay_state.state,
            "valeur": relay_state.valeur,
            "battery_id": battery.id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": "Une erreur s'est produite lors de la récupération de l'état du relais",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# =============================================graphique==============================


# ========================================
# APIs pour BATTERY
# ========================================

@api_view(["GET"])
def get_daily_battery_data(request, module_id, week_number=None, day_of_week=None):
    """
    API pour récupérer les données journalières des batteries.
    """
    
    try:
        target_date = _calculate_target_date(week_number, day_of_week)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        # Récupérer les données battery
        battery_data = BatteryData.objects.filter(
            battery__module_id=module_id,
            createdAt__range=(start_of_day, end_of_day)
        ).order_by("createdAt").values(
            "createdAt", "tension", "puissance", "courant", "energy", "pourcentage"
        )
        
        # Formater les données
        result = []
        for entry in battery_data:
            created_at = entry["createdAt"]
            hour_decimal = created_at.hour + (created_at.minute / 60.0) + (created_at.second / 3600.0)
            
            data_point = {
                "timestamp": created_at.isoformat(),
                "hour_decimal": round(hour_decimal, 3),
                "hour_label": created_at.strftime("%H:%M:%S"),
                "date_label": created_at.strftime("%d/%m/%Y"),
                "tension": float(entry["tension"]) if entry["tension"] else 0.0,
                "puissance": float(entry["puissance"]) if entry["puissance"] else 0.0,
                "courant": float(entry["courant"]) if entry["courant"] else 0.0,
                "energy": float(entry["energy"]) if entry["energy"] else 0.0,
                "pourcentage": float(entry["pourcentage"]) if entry["pourcentage"] else 0.0,
            }
            result.append(data_point)
        
        response_data = {
            "component_type": "battery",
            "module_id": module_id,
            "date": target_date.strftime("%Y-%m-%d"),
            "day_name": _get_french_day_name(target_date.strftime("%A")),
            "week_number": target_date.isocalendar()[1],
            "total_records": len(result),
            "last_updated": timezone.now().isoformat(),
            "data_range": {
                "start": start_of_day.isoformat(),
                "end": end_of_day.isoformat()
            },
            "data": result
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error retrieving battery data: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])  
def get_realtime_battery_data(request, module_id):
    """
    API pour récupérer les données battery en temps réel (dernières 24h).
    """
    
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    try:
        # Récupérer les données des dernières 24h
        queryset = BatteryData.objects.filter(
            battery__module_id=module_id,
            createdAt__gte=today_start,
            createdAt__lte=now
        ).order_by("createdAt")
        
        # Formater les données
        data = []
        for entry in queryset:
            created_at = entry.createdAt
            # hour_decimal = created_at.hour + (created_at.minute / 60.0) + (created_at.second / 3600.0)
            
            formatted_entry = {
                "timestamp": created_at.isoformat(),
                # "hour_decimal": round(hour_decimal, 3),
                "hour_label": created_at.strftime("%H:%M"),
                # "date_label": created_at.strftime("%d/%m/%Y"),
                "tension": float(entry.tension,0),
                "puissance": float(entry.puissance,0),
                "courant": float(entry.courant,0),
                "energy": float(entry.energy,0),
                "pourcentage": float(entry.pourcentage,0) ,
            }
            data.append(formatted_entry)
        
        # data.reverse()
        
        response_data = {
            "component_type": "battery",
            "module_id": module_id,
            "realtime": True,
            "data_period": 24,
            "total_records": len(data),
            "last_updated": now.isoformat(),
            "refresh_interval": 30,
            "data": data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error retrieving realtime battery data: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_battery_statistics(request, module_id):
    """
    API pour récupérer les statistiques du jour pour les batteries.
    """
    
    try:
        today = timezone.now().date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        # Récupérer les données du jour
        battery_data = BatteryData.objects.filter(
            battery__module_id=module_id,
            createdAt__range=(start_of_day, end_of_day)
        ).values("tension", "puissance", "courant", "energy", "pourcentage")
        
        if not battery_data:
            return Response({
                "component_type": "battery",
                "date": today.strftime("%Y-%m-%d"),
                "statistics": {
                    "total_records": 0,
                    "message": "No data available for today"
                }
            })
        
        # Calculer les statistiques
        metrics = ['tension', 'puissance', 'courant', 'energy', 'pourcentage']
        statistics = {}
        
        for metric in metrics:
            values = [float(entry[metric]) for entry in battery_data if entry[metric]]
            if values:
                statistics[metric] = {
                    "current": values[-1],
                    "min": min(values),
                    "max": max(values),
                    "avg": round(sum(values) / len(values), 2),
                    "total": round(sum(values), 2) if metric == 'energy' else None
                }
        
        response_data = {
            "component_type": "battery",
            "module_id": module_id,
            "date": today.strftime("%Y-%m-%d"),
            "total_records": len(battery_data),
            "statistics": statistics,
            "last_updated": timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error calculating battery statistics: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

