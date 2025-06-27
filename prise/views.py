from rest_framework import status

# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, F, FloatField
from django.db.models.functions import ExtractMonth
from django.db.models.functions import Cast
from datetime import datetime
from datetime import datetime, timedelta
from calendar import monthrange
from django.db.models.functions import ExtractWeek, ExtractWeekDay
from datetime import timezone
# utils
from users.utils import _calculate_target_date,_get_french_day_name

# models
from .models import Prise
from .models import PriseData
from .models import PrisePlanning
from .models import PriseReference
from .models import PriseRelaiState
from module.models import Modules

# serializer
from .serializers import PriseSerializer
from .serializers import PriseDataSerializer
from .serializers import PrisePlanningSerializer
from .serializers import PriseReferenceSerializer
from .serializers import PriseRelaiStateSerializer
from .serializers import PriseAllSerializer


# view

@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_Prise(request):
    prise = Prise.objects.all().order_by("-createdAt")
    serializer = PriseAllSerializer(Prise, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_Prise_by_module(request, module_id):
    try:
        prise = Prise.objects.get(module__id=module_id)
        serializer = PriseSerializer(prise, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Prise.DoesNotExist:
        return Response(
            {"error": "prise not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

# Prise APIView
class PriseAPIView(APIView):

    def get_object(self, prise_id):
        try:
            return Prise.objects.get(id=prise_id)
        except Prise.DoesNotExist:
            return Response(
                {"error": "Prise not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        name = request.data.get("name")
        voltage = request.data.get("voltage")
        module = request.data.get("module")


        if module is None or name is None or voltage is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

         # module
        if Prise.objects.filter(module__id=module).exists():
            return Response(
                {"error": "prise already existe"}, status=status.HTTP_400_BAD_REQUEST
            )


        # get module
        module_data = get_object_or_404(Modules, id=module)

        # create user
        prise = Prise.objects.create(
            name=name,
            voltage=voltage,
            module=module_data,
        )
        # save into database
        prise.save()

        serializer = PriseSerializer(prise, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, prise_id):
        prise = self.get_object(prise_id=prise_id)
        serializer = PriseSerializer(prise, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, prise_id):
        prise = self.get_object(prise_id=prise_id)
        # variables
        voltage = request.data.get("voltage")
        name = request.data.get("name")
        #  name
        if name:
            prise.name = name
            prise.save()

        #  voltage
        if voltage:
            prise.voltage = voltage
            prise.save()

        serializer = PriseSerializer(prise, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, prise_id):
        prise = self.get_object(prise_id=prise_id)
        prise.delete()
        return Response(
            {"message": "Prise is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# get all PriseData PriseDataSerializer
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_PriseData_by_prise(request, prise_id):
    prise_data = PriseData.objects.filter(prise__id=prise_id)
    serializer = PriseDataSerializer(prise_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#  PriseData PriseDataSerializer APIView
class PriseDataAPIView(APIView):

    def get_object(self, prise_data_id):
        try:
            return PriseData.objects.get(id=prise_data_id)
        except PriseData.DoesNotExist:
            return Response(
                {"error": "Prise Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        tension = request.data.get("tension")
        puissance = request.data.get("puissance")
        courant = request.data.get("courant")
        consomation = request.data.get("consomation")
        prise_id = request.data.get("prise_id")

        if (
            tension is None
            or puissance is None
            or courant is None
            or consomation is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get Prise
        prise = get_object_or_404(Prise, id=prise_id)

        prise_data = PriseData.objects.create(
            tension=tension,
            prise=prise,
            puissance=puissance,
            courant=courant,
            consomation=consomation,
        )
        # save into database
        prise_data.save()
        serializer = PriseDataSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, prise_data_id):
        prise_data = self.get_object(prise_data_id=prise_data_id)
        serializer = PriseDataSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, prise_data_id):
        prise_data = self.get_object(prise_data_id=prise_data_id)
        # variables
        tension = request.data.get("tension")
        puissance = request.data.get("puissance")
        courant = request.data.get("courant")
        consomation = request.data.get("consomation")

        #  tension
        if tension:
            prise_data.tension = tension
            prise_data.save()

        #  puissance
        if puissance:
            prise_data.puissance = puissance
            prise_data.save()

        #  courant
        if courant:
            prise_data.courant = courant
            prise_data.save()

        #  consomation
        if consomation:
            prise_data.consomation = consomation
            prise_data.save()

        serializer = PriseDataSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, prise_data_id):
        prise = self.get_object(prise_data_id=prise_data_id)
        prise.delete()
        return Response(
            {"message": "Prise data is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# get all PrisePlanning
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_PrisePlanning_by_Prise(request, prise_id):
    prise_data = PrisePlanning.objects.filter(prise__id=prise_id)
    serializer = PrisePlanningSerializer(prise_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# plannig by module
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_PrisePlanning_by_module(request, module_id):
    module_data = get_object_or_404(Modules, id=module_id)
    prise_value = get_object_or_404(Prise, module=module_data.id)
    prise_data = PrisePlanning.objects.filter(prise__id=prise_value.id)
    serializer = PrisePlanningSerializer(prise_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



#  PrisePlanning PrisePlanningSerializer APIView
class PrisePlanningPIView(APIView):

    def get_object(self, prise_planning_id):
        try:
            return PrisePlanning.objects.get(id=prise_planning_id)
        except PrisePlanning.DoesNotExist:
            return Response(
                {"error": "Prise planning Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        consomation = request.data.get("consomation")
        date_debut = request.data.get("date_debut")
        date_fin = request.data.get("date_fin")
        date = request.data.get("date")
        done = request.data.get("done")
        prise_id = request.data.get("prise_id")

        if (
            consomation is None
            or date_debut is None
            or date_fin is None
            or done is None
            or prise_id is None
            or date is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get Prise
        prise = get_object_or_404(Prise, id=prise_id)

        pannau_data = PrisePlanning.objects.create(
            consomation=consomation,
            prise=prise,
            date_debut=date_debut,
            date_fin=date_fin,
            date=date,
            done=done,
        )
        # save into database
        pannau_data.save()
        serializer = PrisePlanningSerializer(pannau_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, prise_planning_id):
        prise = self.get_object(prise_planning_id=prise_planning_id)
        serializer = PrisePlanningSerializer(prise, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, prise_planning_id):
        prise_data = self.get_object(prise_planning_id=prise_planning_id)
        # variables
        consomation = request.data.get("consomation")
        date_debut = request.data.get("date_debut")
        date_fin = request.data.get("date_fin")
        done = request.data.get("done")
        date = request.data.get("date")

        #  consomation
        if consomation:
            prise_data.consomation = consomation
            prise_data.save()

        #  date_debut
        if date_debut:
            prise_data.date_debut = date_debut
            prise_data.save()

        #  date_fin
        if date_fin:
            prise_data.date_fin = date_fin
            prise_data.save()

        #  done
        if done:
            prise_data.done = done
            prise_data.save()

        #  date
        if date:
            prise_data.date = date
            prise_data.save()

        serializer = PrisePlanningSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, prise_planning_id):
        prise = self.get_object(prise_planning_id=prise_planning_id)
        prise.delete()
        return Response(
            {"message": "Prise planning is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


# PriseRelaiState PriseRelaiStateSerializer
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_PriseRelaiState_by_Prise(request, prise_id):
    prise_data = PriseRelaiState.objects.filter(prise__id=prise_id).first()
    serializer = PriseRelaiStateSerializer(prise_data, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def switch_PriseRelaiState_by_Prise(request, prise_id):
    if not prise_id:
        return Response(
            {"detail": "Prise ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if the prise exists
    prise = get_object_or_404(Prise, id=prise_id)
    relai_state = get_object_or_404(PriseRelaiState, prise=prise)


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
    serializer = PriseRelaiStateSerializer(relai_state, many=False)

    # Return the new state
    return Response(serializer.data,
        status=status.HTTP_200_OK,
    )


#  PriseRelaiState APIView
class PriseRelaiStateAPIView(APIView):

    def get_object(self, prise_relai_id):
        try:
            return PriseRelaiState.objects.get(id=prise_relai_id)
        except PriseRelaiState.DoesNotExist:
            return Response(
                {"error": " Prise Relai State Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        active = request.data.get("active")
        state = request.data.get("state")
        couleur = request.data.get("couleur")
        valeur = request.data.get("valeur")
        prise_id = request.data.get("prise_id")

        if (
            active is None
            or state is None
            or couleur is None
            or valeur is None
            or prise_id is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

        if active =="true":
            active=True
        else:
            active= False


        # get Prise
        prise = get_object_or_404(Prise, id=prise_id)

        prise_data = PriseRelaiState.objects.create(
            active=active,
            prise=prise,
            state=state,
            couleur=couleur,
            valeur=valeur,
        )
        # save into database
        prise_data.save()
        serializer = PriseRelaiStateSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, prise_relai_id):
        prise_data = self.get_object(prise_relai_id=prise_relai_id)
        serializer = PriseRelaiStateSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, prise_relai_id):
        prise_data = self.get_object(prise_relai_id=prise_relai_id)
        # variables
        active = request.data.get("active")
        state = request.data.get("state")
        couleur = request.data.get("couleur")
        valeur = request.data.get("valeur")

        #  active
        if active:
            prise_data.active = active
            prise_data.save()

        #  state
        if state:
            prise_data.state = state
            prise_data.save()

        #  couleur
        if couleur:
            prise_data.couleur = couleur
            prise_data.save()

        #  valeur
        if valeur:
            prise_data.valeur = valeur
            prise_data.save()

        serializer = PriseRelaiStateSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, prise_relai_id):
        prise_data = self.get_object(prise_relai_id=prise_relai_id)
        prise_data.delete()
        return Response(
            {"message": "prise planning is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


# PriseReference  PriseReferenceSerializer
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_PriseReference_by_prise(request, prise_id):
    prise_data = PriseReference.objects.filter(prise__id=prise_id)
    serializer = PriseReferenceSerializer(prise_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class PriseReferenceAPIView(APIView):

    def get_object(self, prise_reference_id):
        try:
            return PriseReference.objects.get(id=prise_reference_id)
        except PriseReference.DoesNotExist:
            return Response(
                {"error": " prise reference Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        checked_data = request.data.get("checked_data")
        checked_state = request.data.get("checked_state")
        duration = request.data.get("duration")
        energy = request.data.get("energy")
        prise_id = request.data.get("prise_id")

        if (
            checked_data is None
            or checked_state is None
            or duration is None
            or energy is None
            or prise_id is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get prise
        prise = get_object_or_404(prise, id=prise_id)

        prise_data = PriseReference.objects.create(
            checked_data=checked_data,
            prise=prise,
            checked_state=checked_state,
            duration=duration,
            energy=energy,
        )
        # save into database
        prise_data.save()
        serializer = PriseReferenceSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, prise_reference_id):
        prise_data = self.get_object(prise_reference_id=prise_reference_id)
        serializer = PriseReferenceSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, prise_reference_id):
        prise_data = self.get_object(prise_reference_id=prise_reference_id)
        # variables
        checked_data = request.data.get("checked_data")
        checked_state = request.data.get("checked_state")
        duration = request.data.get("duration")
        energy = request.data.get("energy")

        #  consomation
        if checked_data:
            prise_data.checked_data = checked_data
            prise_data.save()

        #  checked_state
        if checked_state:
            prise_data.checked_state = checked_state
            prise_data.save()

        #  duration
        if duration:
            prise_data.duration = duration
            prise_data.save()

        #  energy
        if energy:
            prise_data.energy = energy
            prise_data.save()

        serializer = PriseReferenceSerializer(prise_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, prise_reference_id):
        prise = self.get_object(prise_reference_id=prise_reference_id)
        prise.delete()
        return Response(
            {"message": "prise reference is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )

# auto
@receiver(post_save, sender=Prise)
def create_relai_state_auto_prise(sender, instance, created, **kwargs):
    if created:
        # create
        relay=PriseRelaiState.objects.create(
            prise= instance,
            active= False,
            state= "low",
            couleur= "green",
            valeur="0"
        )
        relay.save()
# ====================mobile=====================
@api_view(["GET"])
def get_couleur_prise_by_id_module(request, module_id):
    """
    Endpoint DRF pour obtenir les couleurs des prises associées à un module spécifique.

    :param request: Objet de requête
    :param module_id: ID du module (passé dans l'URL)
    :return: JSON contenant les couleurs des prises ou un message d'erreur
    """
    try:
        # Vérifier si le module existe
        module = Modules.objects.get(id=module_id)

        # Récupérer les prises associées au module et leurs couleurs via PriseRelaiState
        prises_relai_state = PriseRelaiState.objects.filter(prise__module=module).first()

        # Extraire les couleurs des prises
        serializer = PriseRelaiStateSerializer(prises_relai_state,many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Modules.DoesNotExist:
        return Response(
            {"error": "Le module avec l'ID spécifié n'existe pas."},
            status=status.HTTP_404_NOT_FOUND,
        )



@api_view(["GET"])
def get_consommation_prise_annuelle(request,module_id):

    # Validate that `module_id` is provided
    if not module_id:
        return Response({"detail": "Module ID is required."}, status=400)

    try:
        # Récupérer la prise correspondante
        module = get_object_or_404(Modules, id=module_id)
        prise = get_object_or_404(Prise, module=module)

        # Année en cours
        current_year = datetime.now().year

        # Récupérer et regrouper les données par mois
        monthly_data = (
            PriseData.objects.filter(prise=prise, createdAt__year=current_year)
            .annotate(month=ExtractMonth("createdAt"))  # Extraire le mois
            .values("month")
            .annotate(
                total_consumption=Sum(Cast("consomation", FloatField())),  # Somme de la consommation mensuelle
                total_voltage=Sum(Cast("tension", FloatField())),  # Somme des tensions mensuelles (facultatif)
                total_current=Sum(Cast("courant", FloatField())),  # Somme des courants mensuels (facultatif)
            )
            .order_by("month")
        )

        # Initialiser les labels et les données
        labels = [i for i in range(1, 13)]  # Mois de 1 (Janvier) à 12 (Décembre)
        data = [0] * 12  # Initialiser une liste avec 12 zéros

        # Remplir les données
        for entry in monthly_data:
            month_index = entry["month"] - 1  # L'index commence à 0 pour Janvier
            data[month_index] = entry["total_consumption"]

        # Préparer la réponse
        response_data = {
            "labels": labels,
            "data": data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except PriseData.DoesNotExist:
        return Response(
            {"error": "Aucune donnée trouvée pour la prise spécifiée."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def get_socket_consumption_by_week(request,module_id):
    """
    Retrieve socket consumption for each day of the current week, aggregated by day.
    """
    # Récupérer l'année et la semaine actuelle
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi de cette semaine
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche de cette semaine

    # Récupérer les données de consommation par jour de la semaine
    # # Cast("tension", FloatField())
    data = (
        PriseData.objects.filter(
            prise__module_id=module_id,
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
def get_weekly_prise_data_for_month(request, module_id, year, month):
    """
    Retrieve energy consumption for each week of a given month, aggregated by day of the week for a specific Prise.
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

    # Récupérer les données de la base de données
    # # Cast("tension", FloatField())
    #
    data = (
        PriseData.objects.filter(
            prise__module_id=module_id,
            createdAt__gte=start_of_month,
            createdAt__lte=end_of_month,
        )
        .annotate(
            week=ExtractWeek("createdAt"),
            day_of_week=ExtractWeekDay("createdAt")
        )
        .values("week", "day_of_week")
        .annotate(total_consumption=Sum(Cast("consomation", FloatField())))
        .order_by("week", "day_of_week")
    )

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


@api_view(["GET"])
def get_daily_prise_data_for_week(request, module_id, week_number, day_of_week):
    """
    Retrieve real Prise data for a specific day with exact timestamps.
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

    # Récupérer toutes les données réelles de prise pour cette journée
    prise_data = PriseData.objects.filter(
        prise__module_id=module_id,
        createdAt__range=(start_of_day, end_of_day),
    ).order_by("createdAt").values(
        "createdAt", "tension", "puissance", "courant", "consomation"
    )

    # Convertir les données au format professionnel pour les graphiques
    result = []
    for entry in prise_data:
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
            "consomation": float(entry["consomation"]) if entry["consomation"] else 0.0,
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
def get_prise_relay_state_by_module(request, module_id):
    """
    Récupère l'état du relais de la prise pour un module donné
    """
    try:
        # Vérifier si le module existe
        module = get_object_or_404(Modules, id=module_id)

        # Récupérer la prise associée au module
        prise = Prise.objects.filter(module=module).first()

        if not prise:
            return Response({
                "couleur": "gray",
                "active": False,
                "message": "Aucune prise trouvée pour ce module"
            }, status=status.HTTP_200_OK)

        # Récupérer l'état du relais de la prise
        relay_state = PriseRelaiState.objects.filter(prise=prise).first()

        if not relay_state:
            # Créer un état par défaut si aucun n'existe
            relay_state = PriseRelaiState.objects.create(
                prise=prise,
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
            "prise_id": prise.id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "error": "Une erreur s'est produite lors de la récupération de l'état du relais",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ====================================================graphique

# ========================================
# APIs pour PRISE
# ========================================

@api_view(["GET"])
def get_daily_prise_data(request, module_id, week_number=None, day_of_week=None):
    """
    API pour récupérer les données journalières des prises.
    """
    
    try:
        target_date = _calculate_target_date(week_number, day_of_week)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        # Récupérer les données prise
        prise_data = PriseData.objects.filter(
            prise__module_id=module_id,
            createdAt__range=(start_of_day, end_of_day)
        ).order_by("createdAt").values(
            "createdAt", "tension", "puissance", "courant", "consomation"
        )
        
        # Formater les données
        result = []
        for entry in prise_data:
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
                "consommation": float(entry["consomation"]) if entry["consomation"] else 0.0,  # Note: typo dans le modèle
            }
            result.append(data_point)
        
        response_data = {
            "component_type": "prise",
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
            "error": f"Error retrieving prise data: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])  
def get_realtime_prise_data(request, module_id):
    """
    API pour récupérer les données prise en temps réel (dernières 24h).
    """
    
    now = timezone.now()
    yesterday = now - timedelta(hours=24)
    
    try:
        # Récupérer les données des dernières 24h
        queryset = PriseData.objects.filter(
            prise__module_id=module_id,
            createdAt__gte=yesterday
        ).order_by("-createdAt")[:100]
        
        # Formater les données
        data = []
        for entry in queryset:
            created_at = entry.createdAt
            hour_decimal = created_at.hour + (created_at.minute / 60.0) + (created_at.second / 3600.0)
            
            formatted_entry = {
                "timestamp": created_at.isoformat(),
                "hour_decimal": round(hour_decimal, 3),
                "hour_label": created_at.strftime("%H:%M:%S"),
                "date_label": created_at.strftime("%d/%m/%Y"),
                "tension": float(entry.tension) if entry.tension else 0.0,
                "puissance": float(entry.puissance) if entry.puissance else 0.0,
                "courant": float(entry.courant) if entry.courant else 0.0,
                "consommation": float(entry.consomation) if entry.consomation else 0.0,
            }
            data.append(formatted_entry)
        
        data.reverse()
        
        response_data = {
            "component_type": "prise",
            "module_id": module_id,
            "realtime": True,
            "data_period": "24h",
            "total_records": len(data),
            "last_updated": now.isoformat(),
            "refresh_interval": 30,
            "data": data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error retrieving realtime prise data: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_prise_statistics(request, module_id):
    """
    API pour récupérer les statistiques du jour pour les prises.
    """
    
    try:
        today = timezone.now().date()
        start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        # Récupérer les données du jour
        prise_data = PriseData.objects.filter(
            prise__module_id=module_id,
            createdAt__range=(start_of_day, end_of_day)
        ).values("tension", "puissance", "courant", "consomation")
        
        if not prise_data:
            return Response({
                "component_type": "prise",
                "date": today.strftime("%Y-%m-%d"),
                "statistics": {
                    "total_records": 0,
                    "message": "No data available for today"
                }
            })
        
        # Calculer les statistiques
        metrics = ['tension', 'puissance', 'courant', 'consomation']
        statistics = {}
        
        for metric in metrics:
            values = [float(entry[metric]) for entry in prise_data if entry[metric]]
            if values:
                stat_key = "consommation" if metric == "consomation" else metric
                statistics[stat_key] = {
                    "current": values[-1],
                    "min": min(values),
                    "max": max(values),
                    "avg": round(sum(values) / len(values), 2),
                    "total": round(sum(values), 2) if metric == 'consomation' else None
                }
        
        response_data = {
            "component_type": "prise",
            "module_id": module_id,
            "date": today.strftime("%Y-%m-%d"),
            "total_records": len(prise_data),
            "statistics": statistics,
            "last_updated": timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "error": f"Error calculating prise statistics: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

