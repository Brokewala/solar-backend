from rest_framework import status
# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.functions import Cast
from django.db.models import Sum, FloatField
from django.db.models.functions import ExtractMonth
from datetime import datetime, timedelta
from django.db.models.functions import ExtractWeek, ExtractWeekDay
from calendar import monthrange
# from datetime import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# utils
from users.utils import _calculate_target_date,_get_french_day_name

# models
from .models import Panneau
from .models import PanneauData
from .models import PanneauPlanning
from .models import PanneauReference
from .models import PanneauRelaiState
from module.models import Modules

# serializer
from .serializers import PanneauSerializer
from .serializers import PanneauDataSerializer
from .serializers import PanneauPlanningSerializer
from .serializers import PanneauReferenceSerializer
from .serializers import PanneauRelaiStateSerializer
from .serializers import PenneauAllSerializer
from solar_backend.timezone_utils import (
    local_day_bounds,
    local_month_bounds,
    local_now,
    local_today,
)


@swagger_auto_schema(
    method='get',
    operation_description="Récupère tous les panneaux solaires avec leurs données complètes",
    responses={
        200: PenneauAllSerializer(many=True),
        400: 'Bad Request',
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_panneau(request):
    panneau = Panneau.objects.all().order_by("-createdAt")
    serializer = PenneauAllSerializer(panneau, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Récupère un panneau solaire spécifique par l'ID du module",
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
        200: PanneauSerializer,
        404: openapi.Response('Panneau non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_panneau_by_module(request, module_id):
    try:
        panneau = Panneau.objects.get(module__id=module_id)
        serializer = PanneauSerializer(panneau, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Panneau.DoesNotExist:
        return Response(
            {"error": "panneau not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

# Panneau APIView
class PanneauAPIView(APIView):

    def get_object(self, panneau_id):
        try:
            return Panneau.objects.get(id=panneau_id)
        except Panneau.DoesNotExist:
            return Response(
                {"error": "panneau not found"},
                status=status.HTTP_404_NOT_FOUND,
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
        if Panneau.objects.filter(module__id=module).exists():
            return Response(
                {"error": "panneau already existe"}, status=status.HTTP_400_BAD_REQUEST
            )

        # get module
        module_data = get_object_or_404(Modules, id=module)

        # create user
        panneau = Panneau.objects.create(
            puissance=puissance,
            voltage=voltage,
            marque=marque,
            module=module_data,
        )
        # save into database
        panneau.save()

        serializer = PanneauSerializer(panneau, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, panneau_id):
        panneau = self.get_object(panneau_id=panneau_id)
        serializer = PanneauSerializer(panneau, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, panneau_id):
        panneau = self.get_object(panneau_id=panneau_id)
        # variables
        puissance = request.data.get("puissance")
        voltage = request.data.get("voltage")
        marque = request.data.get("marque")
        #  puissance
        if puissance:
            panneau.puissance = puissance
            panneau.save()

        #  voltage
        if voltage:
            panneau.voltage = voltage
            panneau.save()

        #  marque
        if marque:
            panneau.marque = marque
            panneau.save()

        serializer = PanneauSerializer(panneau, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, panneau_id):
        panneau = self.get_object(panneau_id=panneau_id)
        panneau.delete()
        return Response(
            {"message": "panneau is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# get all PanneauData PanneauDataSerializer
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_PanneauData_by_panneau(request, panneau_id):
    panneau_data = PanneauData.objects.filter(panneau__id=panneau_id)
    serializer = PanneauDataSerializer(panneau_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#  PanneauData PanneauDataSerializer APIView
class PanneauDataAPIView(APIView):

    def get_object(self, panneau_data_id):
        try:
            return PanneauData.objects.get(id=panneau_data_id)
        except PanneauData.DoesNotExist:
            return Response(
                {"error": "panneau Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        tension = request.data.get("tension")
        puissance = request.data.get("puissance")
        courant = request.data.get("courant")
        production = request.data.get("production")
        panneau_id = request.data.get("panneau_id")

        if (
            tension is None
            or puissance is None
            or courant is None
            or production is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get panneau
        panneau = get_object_or_404(Panneau, id=panneau_id)

        panneau_data = PanneauData.objects.create(
            tension=tension,
            panneau=panneau,
            puissance=puissance,
            courant=courant,
            production=production,
        )
        # save into database
        panneau_data.save()
        print("======================panneau_data===========",panneau_data.createdAt)
        serializer = PanneauDataSerializer(panneau_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, panneau_data_id):
        module = self.get_object(panneau_data_id=panneau_data_id)
        serializer = PanneauDataSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, panneau_data_id):
        panneau_data = self.get_object(panneau_data_id=panneau_data_id)
        # variables
        tension = request.data.get("tension")
        puissance = request.data.get("puissance")
        courant = request.data.get("courant")
        production = request.data.get("production")

        #  tension
        if tension:
            panneau_data.tension = tension
            panneau_data.save()

        #  puissance
        if puissance:
            panneau_data.puissance = puissance
            panneau_data.save()

        #  courant
        if courant:
            panneau_data.courant = courant
            panneau_data.save()

        #  production
        if production:
            panneau_data.production = production
            panneau_data.save()

        serializer = PanneauDataSerializer(panneau_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, panneau_data_id):
        panneau = self.get_object(panneau_data_id=panneau_data_id)
        panneau.delete()
        return Response(
            {"message": "panneau data is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# get all PanneauPlanning
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_PanneauPlanning_by_panneau(request, panneau_id):
    panneau_data = PanneauPlanning.objects.filter(panneau__id=panneau_id)
    serializer = PanneauPlanningSerializer(panneau_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# plannig by module
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_PanneauPlanning_by_module(request, module_id):
    module_data = get_object_or_404(Modules, id=module_id)
    panneau_value = get_object_or_404(Panneau, module=module_data.id)
    panneau_data = PanneauPlanning.objects.filter(panneau__id=panneau_value.id)
    serializer = PanneauPlanningSerializer(panneau_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#  PanneauPlanning PanneauPlanningSerializer APIView
class PanneauPlanningPIView(APIView):

    def get_object(self, panneau_planning_id):
        try:
            return PanneauPlanning.objects.get(id=panneau_planning_id)
        except PanneauPlanning.DoesNotExist:
            return Response(
                {"error": "panneau planning Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        energie = request.data.get("energie")
        date_debut = request.data.get("date_debut")
        date_fin = request.data.get("date_fin")
        done = request.data.get("done")
        panneau_id = request.data.get("panneau_id")

        if (
            energie is None
            or date_debut is None
            or date_fin is None
            or done is None
            or panneau_id is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get panneau
        panneau = get_object_or_404(Panneau, id=panneau_id)

        pannau_data = PanneauPlanning.objects.create(
            energie=energie,
            panneau=panneau,
            date_debut=date_debut,
            date_fin=date_fin,
            done=done,
        )
        # save into database
        pannau_data.save()
        serializer = PanneauPlanningSerializer(pannau_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, panneau_planning_id):
        panneau = self.get_object(panneau_planning_id=panneau_planning_id)
        serializer = PanneauPlanningSerializer(panneau, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, panneau_planning_id):
        panneau_data = self.get_object(panneau_planning_id=panneau_planning_id)
        # variables
        energie = request.data.get("energie")
        date_debut = request.data.get("date_debut")
        date_fin = request.data.get("date_fin")
        done = request.data.get("done")

        #  energie
        if energie:
            panneau_data.energie = energie
            panneau_data.save()

        #  date_debut
        if date_debut:
            panneau_data.date_debut = date_debut
            panneau_data.save()

        #  date_fin
        if date_fin:
            panneau_data.date_fin = date_fin
            panneau_data.save()

        #  done
        if done:
            panneau_data.done = done
            panneau_data.save()

        serializer = PanneauPlanningSerializer(panneau_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, panneau_planning_id):
        panneau = self.get_object(panneau_planning_id=panneau_planning_id)
        panneau.delete()
        return Response(
            {"message": "panneau planning is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


# PanneauRelaiState PanneauRelaiStateSerializer
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_PanneauRelaiState_by_panneau(request, panneau_id):
    panneau_data = PanneauRelaiState.objects.filter(panneau__id=panneau_id)
    serializer = PanneauRelaiStateSerializer(panneau_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def switch_panneauRelaiState_by_panneau(request, panneau_id):
    if not panneau_id:
        return Response(
            {"detail": "panneau ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if the battery exists
    panneau_value = get_object_or_404(Panneau, id=panneau_id)
    relai_state = get_object_or_404(PanneauRelaiState, panneau=panneau_value)


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
    serializer = PanneauRelaiStateSerializer(relai_state, many=False)

    # Return the new state
    return Response(serializer.data,
        status=status.HTTP_200_OK,
    )



#  PanneauRelaiState APIView
class PanneauRelaiStateAPIView(APIView):

    def get_object(self, panneau_relai_id):
        try:
            return PanneauRelaiState.objects.get(id=panneau_relai_id)
        except PanneauRelaiState.DoesNotExist:
            return Response(
                {"error": " panneau Relai State Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        active = request.data.get("active")
        state = request.data.get("state")
        couleur = request.data.get("couleur")
        valeur = request.data.get("valeur")
        panneau_id = request.data.get("panneau_id")

        if (
            active is None
            or state is None
            or couleur is None
            or valeur is None
            or panneau_id is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get panneau
        panneau = get_object_or_404(Panneau, id=panneau_id)

        panneau_data = PanneauRelaiState.objects.create(
            active=active,
            panneau=panneau,
            state=state,
            couleur=couleur,
            valeur=valeur,
        )
        # save into database
        panneau_data.save()
        serializer = PanneauRelaiStateSerializer(panneau_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, panneau_relai_id):
        panneau_data = self.get_object(panneau_relai_id=panneau_relai_id)
        serializer = PanneauRelaiStateSerializer(panneau_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, panneau_relai_id):
        panneau_data = self.get_object(panneau_relai_id=panneau_relai_id)
        # variables
        active = request.data.get("active")
        state = request.data.get("state")
        couleur = request.data.get("couleur")
        valeur = request.data.get("valeur")

        #  active
        if active:
            panneau_data.active = active
            panneau_data.save()

        #  state
        if state:
            panneau_data.state = state
            panneau_data.save()

        #  couleur
        if couleur:
            panneau_data.couleur = couleur
            panneau_data.save()

        #  valeur
        if valeur:
            panneau_data.valeur = valeur
            panneau_data.save()

        serializer = PanneauRelaiStateSerializer(panneau_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, panneau_relai_id):
        panneau = self.get_object(panneau_relai_id=panneau_relai_id)
        panneau.delete()
        return Response(
            {"message": "panneau planning is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


class PanneauRelaiStateAPIViewIOT(APIView):
    """
    GET  -> récupérer l'état du relai via panneau_id
    PUT  -> modifier l'état du relai via panneau_id
    """

    def get(self, request, panneau_id):
        relai_state = get_object_or_404(PanneauRelaiState, panneau__id=panneau_id)
        serializer = PanneauRelaiStateSerializer(relai_state)
        return Response(serializer.data)

    def post(self, request, panneau_id):
        relai_state = get_object_or_404(PanneauRelaiState, panneau__id=panneau_id)
        serializer = PanneauRelaiStateSerializer(relai_state, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

# PanneauReference  PanneauReferenceSerializer
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_PanneauReference_by_panneau(request, panneau_id):
    panneau_data = PanneauReference.objects.filter(panneau__id=panneau_id)
    serializer = PanneauReferenceSerializer(panneau_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class PanneauReferenceAPIView(APIView):

    def get_object(self, panneau_reference_id):
        try:
            return PanneauReference.objects.get(id=panneau_reference_id)
        except PanneauReference.DoesNotExist:
            return Response(
                {"error": " panneau reference Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        checked_data = request.data.get("checked_data")
        checked_state = request.data.get("checked_state")
        duration = request.data.get("duration")
        energy = request.data.get("energy")
        panneau_id = request.data.get("panneau_id")

        if (
            checked_data is None
            or checked_state is None
            or duration is None
            or energy is None
            or panneau_id is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get panneau
        panneau = get_object_or_404(Panneau, id=panneau_id)

        panneau_data = PanneauReference.objects.create(
            checked_data=checked_data,
            panneau=panneau,
            checked_state=checked_state,
            duration=duration,
            energy=energy,
        )
        # save into database
        panneau_data.save()
        serializer = PanneauReferenceSerializer(panneau_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, panneau_reference_id):
        panneau_data = self.get_object(panneau_reference_id=panneau_reference_id)
        serializer = PanneauReferenceSerializer(panneau_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, panneau_reference_id):
        panneau_data = self.get_object(panneau_reference_id=panneau_reference_id)
        # variables
        checked_data = request.data.get("checked_data")
        checked_state = request.data.get("checked_state")
        duration = request.data.get("duration")
        energy = request.data.get("energy")

        #  energie
        if checked_data:
            panneau_data.checked_data = checked_data
            panneau_data.save()

        #  checked_state
        if checked_state:
            panneau_data.checked_state = checked_state
            panneau_data.save()

        #  duration
        if duration:
            panneau_data.duration = duration
            panneau_data.save()

        #  energy
        if energy:
            panneau_data.energy = energy
            panneau_data.save()

        serializer = PanneauReferenceSerializer(panneau_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, panneau_reference_id):
        panneau = self.get_object(panneau_reference_id=panneau_reference_id)
        panneau.delete()
        return Response(
            {"message": "panneau reference is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )

# auto====================

# PanneauRelaiState create auto
@receiver(post_save, sender=Panneau)
def create_relai_state_auto_panneau(sender, instance, created, **kwargs):
    if created:
        # create
        relay=PanneauRelaiState.objects.create(
            panneau= instance,
            active= False,
            state= "low",
            couleur= "green",
            valeur="0"
        )
        relay.save()

# ===================mobile===========================
@api_view(["GET"])
def couleur_by_module(request,module_id):

    # Check if module_id is provided
    if not module_id:
        return Response({"detail": "Module ID is required"}, status=400)

    # Filtering by module ID
    panneaux = PanneauRelaiState.objects.filter(panneau__module_id=module_id).first()
    serializer = PanneauRelaiStateSerializer(panneaux, many=False)
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(["GET"])
def get_production_panneau_annuelle(request,module_id):

    # Check if module_id is provided
    if not module_id:
        return Response({"detail": "Module ID is required"}, status=400)

    # Filter PanneauData by module_id via related Panneau
    try:
        # Récupérer le panneau spécifié
        module = get_object_or_404(Modules, id=module_id)
        panneau = get_object_or_404(Panneau, module=module)

        # Année en cours
        current_year = local_today().year

        # Récupérer et regrouper les données par mois
        monthly_data = (
            PanneauData.objects.filter(panneau=panneau, createdAt__year=current_year)
            .annotate(month=ExtractMonth("createdAt"))  # Extraire le mois de la date
            .values("month")
            .annotate(
                total_production=Sum(Cast("production", FloatField())),  # Somme de la production par mois
                total_voltage=Sum(Cast("tension", FloatField())),  # Somme de la tension par mois (optionnel)
                total_current=Sum(Cast("courant", FloatField())),  # Somme du courant par mois (optionnel)
            )
            .order_by("month")
        )

        # Initialiser les labels et les données
        labels = [i for i in range(1, 13)]  # Mois de 1 (Janvier) à 12 (Décembre)
        data = [0] * 12  # Initialiser une liste avec 12 zéros

        # Remplir les données avec les résultats des requêtes
        for entry in monthly_data:
            month_index = entry["month"] - 1  # L'index commence à 0 pour Janvier
            data[month_index] = entry["total_production"]

        # Préparer la réponse au format JSON
        response_data = {
            "labels": labels,  # Mois de 1 à 12
            "data": data,      # Données agrégées de production pour chaque mois
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except PanneauData.DoesNotExist:
        return Response(
            {"error": "Aucune donnée trouvée pour le panneau spécifié."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def get_panel_consumption_by_week(request,module_id):
    """
    Retrieve panel consumption for each day of the current week, aggregated by day.
    """
    # Récupérer l'année et la semaine actuelle
    today = local_today()
    start_of_week_date = today - timedelta(days=today.weekday())  # Lundi de cette semaine
    end_of_week_date = start_of_week_date + timedelta(days=6)  # Dimanche de cette semaine
    start_of_week, _ = local_day_bounds(start_of_week_date)
    _, end_of_week = local_day_bounds(end_of_week_date)

    # Récupérer les données de consommation par jour de la semaine
    # Cast("tension", FloatField())
    data = (
        PanneauData.objects.filter(
            panneau__module_id=module_id,
            createdAt__gte=start_of_week,
            createdAt__lte=end_of_week,
        )
        .values("createdAt__weekday")
        .annotate(total_consumption=Sum(Cast("consumption", FloatField())))
        .order_by("createdAt__weekday")
    )

    # Organiser les données pour correspondre aux jours de la semaine (lundi, mardi, etc.)
    week_labels = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    consumption_data = {label: 0 for label in week_labels}

    for entry in data:
        day_of_week = entry["createdAt__weekday"]
        consumption_data[week_labels[day_of_week]] = entry["total_consumption"]

    return Response(consumption_data)


@api_view(["GET"])
def get_weekly_panneau_data_for_month(request, module_id, year, month):
    """
    Retrieve production data for each week of a given month, aggregated by day of the week for a specific Panneau.
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
    start_of_month, end_of_month = local_month_bounds(year, month)
    start_of_month_date = start_of_month.date()
    end_of_month_date = end_of_month.date()

    # Récupérer les données de la base de données
    # Cast("tension", FloatField())
    data = (
        PanneauData.objects.filter(
            panneau__module_id=module_id,
            createdAt__gte=start_of_month,
            createdAt__lte=end_of_month,
        )
        .annotate(
            week=ExtractWeek("createdAt"),
            day_of_week=ExtractWeekDay("createdAt")
        )
        .values("week", "day_of_week")
        .annotate(total_production=Sum(Cast("production", FloatField())))
        .order_by("week", "day_of_week")
    )
    print("==========================================data=====",data)

    # Mapper les jours de la semaine (1 = Dimanche, ..., 7 = Samedi)
    week_labels = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

    # Organisation des données par semaine
    weekly_data = {}
    for entry in data:
        week_number = entry["week"]
        day_of_week = entry["day_of_week"]
        total_production = entry["total_production"]

        # Initialiser les données pour la semaine si nécessaire
        if week_number not in weekly_data:
            weekly_data[week_number] = {"labels": week_labels, "data": [0] * 7}

        # Ajouter la production totale pour le jour de la semaine
        weekly_data[week_number]["data"][day_of_week - 1] = total_production

    # Créer une réponse organisée par semaine
    response_data = []
    for week_number in sorted(weekly_data.keys()):
        response_data.append({
            "week": f"Semaine {week_number}",
            "labels": weekly_data[week_number]["labels"],
            "data": weekly_data[week_number]["data"]
        })

    # Ajouter les semaines sans données
    current_date = start_of_month_date
    while current_date <= end_of_month_date:
        week_number = current_date.isocalendar()[1]  # Récupérer la semaine ISO
        if week_number not in weekly_data:
            response_data.append({
                "week": f"Semaine {week_number}",
                "labels": week_labels,
                "data": [0] * 7
            })
        current_date += timedelta(weeks=1)

    return Response(response_data)


@api_view(["GET"])
def get_daily_panneau_data_for_week(request, module_id, week_number, day_of_week):
    """
    Retrieve real Panneau data for a specific day with exact timestamps.
    Returns all individual data points as inserted by users for accurate daily visualization.
    """
    try:
        week_number = int(week_number)  # Conversion en entier
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

    day_of_week = french_to_english_days.get(day_of_week.lower())
    if not day_of_week:
        return Response(
            {"error": "Invalid day_of_week. Please provide a valid day in French."},
            status=400,
        )

    # Calculer la date du premier jour de l'année
    current_year = local_today().year
    first_day_of_year = datetime(current_year, 1, 1).date()

    # Ajuster pour commencer la semaine un lundi si ce n'est pas le cas
    if first_day_of_year.weekday() != 0:  # 0 = lundi
        first_day_of_year -= timedelta(days=first_day_of_year.weekday())

    # Calculer la date du début de la semaine demandée
    start_of_week_date = first_day_of_year + timedelta(weeks=week_number - 1)

    # Trouver l'index du jour spécifié
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week_index = days_of_week.index(day_of_week)

    # Calculer la date cible
    target_day = start_of_week_date + timedelta(days=day_of_week_index)

    # Plage de temps pour inclure toutes les heures de la journée cible
    start_of_day, end_of_day = local_day_bounds(target_day)

    # Récupérer toutes les données réelles de panneau pour cette journée
    panneau_data = PanneauData.objects.filter(
        panneau__module_id=module_id,
        createdAt__range=(start_of_day, end_of_day),
    ).order_by("createdAt").values(
        "createdAt", "tension", "puissance", "courant", "production"
    )

    # Convertir les données au format professionnel pour les graphiques
    result = []
    for entry in panneau_data:
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
            "production": float(entry["production"]) if entry["production"] else 0.0,
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
def get_panneau_relay_state_by_module(request, module_id):
    """
    Récupère l'état du relais du panneau pour un module donné
    """
    try:
        # Vérifier si le module existe
        module = get_object_or_404(Modules, id=module_id)

        # Récupérer le panneau associé au module
        panneau = Panneau.objects.filter(module=module).first()

        if not panneau:
            return Response({
                "couleur": "gray",
                "active": False,
                "message": "Aucun panneau trouvé pour ce module"
            }, status=status.HTTP_200_OK)

        # Récupérer l'état du relais du panneau
        relay_state = PanneauRelaiState.objects.filter(panneau=panneau).first()

        if not relay_state:
            # Créer un état par défaut si aucun n'existe
            relay_state = PanneauRelaiState.objects.create(
                panneau=panneau,
                active=False,
                state="low",
                couleur="red",
                valeur="0"
            )

        return Response({
            "couleur": relay_state.couleur,
            "active": relay_state.couleur == "green",
            "state": relay_state.state,
            "valeur": relay_state.valeur,
            "panneau_id": str(panneau.id)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": "Une erreur s'est produite lors de la récupération de l'état du relais",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =====================================graphique=======================================

# ========================================
# APIs pour PANNEAU
# ========================================

@api_view(["GET"])
def get_daily_panneau_data(request, module_id, week_number=None, day_of_week=None):
    """
    API pour récupérer les données journalières des panneaux solaires.
    
    Paramètres:
    - module_id: ID du module
    - week_number: numéro de la semaine (optionnel)
    - day_of_week: jour de la semaine en français (optionnel)
    """
    
    try:
        target_date = _calculate_target_date(week_number, day_of_week)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        start_of_day, end_of_day = local_day_bounds(target_date)
        
        # Récupérer les données panneau
        panneau_data = PanneauData.objects.filter(
            panneau__module_id=module_id,
            createdAt__range=(start_of_day, end_of_day)
        ).order_by("createdAt").values(
            "createdAt", "tension", "puissance", "courant", "production"
        )
        
        # Formater les données
        result = []
        for entry in panneau_data:
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
                "production": float(entry["production"]) if entry["production"] else 0.0,
            }
            result.append(data_point)
        
        response_data = {
            "component_type": "panneau",
            "module_id": module_id,
            "date": target_date.strftime("%Y-%m-%d"),
            "day_name": _get_french_day_name(target_date.strftime("%A")),
            "week_number": target_date.isocalendar()[1],
            "total_records": len(result),
            "last_updated": local_now().isoformat(),
            "data_range": {
                "start": start_of_day.isoformat(),
                "end": end_of_day.isoformat()
            },
            "data": result
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error retrieving panneau data: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(["GET"])
def get_panneau_data_filtered(request, module_id):
    """
    API pour récupérer les données journalières d’un panneau solaire.
    
    Filtres possibles :
    - module_id : ID du module (obligatoire)
    - year : année (optionnel, défaut = année actuelle)
    - month : mois (optionnel, défaut = mois actuel)
    - day : jour (optionnel, défaut = jour actuel)
    """

    try:
        # Récupération des filtres dans les query params
        year = request.GET.get("year")
        month = request.GET.get("month")
        day = request.GET.get("day")
        now = local_now()

        # Valeurs par défaut (aujourd'hui)
        year = int(year) if year else now.year
        month = int(month) if month else now.month
        day = int(day) if day else now.day

        # Validation de la date
        try:
            target_date = datetime(year, month, day).date()
        except ValueError:
            return Response(
                {"error": "Date invalide. Vérifiez l'année, le mois et le jour fournis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_of_day, end_of_day = local_day_bounds(target_date)

        # Récupération des données filtrées
        panneau_data = PanneauData.objects.filter(
            panneau__module_id=module_id,
            createdAt__range=(start_of_day, end_of_day)
        ).order_by("createdAt")

        # Formatage des données
        data = []
        for entry in panneau_data:
            created_at = entry.createdAt
            hour_decimal = created_at.hour + (created_at.minute / 60.0)

            data.append({
                "timestamp": created_at.isoformat(),
                "hour_label": created_at.strftime("%H:%M"),
                "hour_decimal": round(hour_decimal, 2),
                "tension": float(entry.tension or 0),
                "puissance": float(entry.puissance or 0),
                "courant": float(entry.courant or 0),
                "production": float(entry.production or 0),
            })

        response_data = {
            "component_type": "panneau",
            "module_id": module_id,
            "date": target_date.strftime("%Y-%m-%d"),
            "year": year,
            "month": month,
            "day": day,
            "total_records": len(data),
            "data_range": {
                "start": start_of_day.isoformat(),
                "end": end_of_day.isoformat(),
            },
            "data": data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Erreur lors de la récupération des données panneau : {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

@api_view(["GET"])  
def get_realtime_panneau_data(request, module_id):
    """
    API pour récupérer les données panneau en temps réel (dernières 24h).
    """
    
    now = local_now()
    # yesterday = now - timedelta(hours=24)
    today_start, _ = local_day_bounds(now)

    try:
        # Récupérer les données des dernières 24h
        queryset = PanneauData.objects.filter(
            panneau__module_id=module_id,
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
                "tension": float(entry.tension or 0),
                "puissance":float(entry.puissance or 0),
                "courant":  float(entry.courant or 0),
                "production": float(entry.production or 0),
            }
            data.append(formatted_entry)
        
        # Inverser pour avoir l'ordre chronologique
        # data.reverse()
        
        response_data = {
            "component_type": "panneau",
            "module_id": module_id,
            "realtime": True,
            "data_period": 24,
            "total_records": len(data),
            "last_updated": now.isoformat(),
            "refresh_interval": 30,  # Secondes
            "data": data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error retrieving realtime panneau data: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_panneau_statistics(request, module_id):
    """
    API pour récupérer les statistiques du jour pour les panneaux.
    """
    
    try:
        today = local_today()
        start_of_day, end_of_day = local_day_bounds(today)
        
        # Récupérer les données du jour
        panneau_data = PanneauData.objects.filter(
            panneau__module_id=module_id,
            createdAt__range=(start_of_day, end_of_day)
        ).values("tension", "puissance", "courant", "production")
        
        if not panneau_data:
            return Response({
                "component_type": "panneau",
                "date": today.strftime("%Y-%m-%d"),
                "statistics": {
                    "total_records": 0,
                    "message": "No data available for today"
                }
            })
        
        # Calculer les statistiques
        metrics = ['tension', 'puissance', 'courant', 'production']
        statistics = {}
        
        for metric in metrics:
            values = [float(entry[metric]) for entry in panneau_data if entry[metric]]
            if values:
                statistics[metric] = {
                    "current": values[-1],
                    "min": min(values),
                    "max": max(values),
                    "avg": round(sum(values) / len(values), 2),
                    "total": round(sum(values), 2) if metric == 'production' else None
                }
        
        response_data = {
            "component_type": "panneau",
            "module_id": module_id,
            "date": today.strftime("%Y-%m-%d"),
            "total_records": len(panneau_data),
            "statistics": statistics,
            "last_updated": local_now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error calculating panneau statistics: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
