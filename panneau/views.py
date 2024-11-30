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
from datetime import datetime
from django.db.models.functions import Cast
from django.db.models import Sum, FloatField
from django.db.models.functions import ExtractMonth
from datetime import datetime, timedelta
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


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_panneau(request):
    panneau = Panneau.objects.all().order_by("-createdAt")
    serializer = PenneauAllSerializer(panneau, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_panneau_by_module(request, module_id):
    panneau = Panneau.objects.get(module__id=module_id)
    serializer = PanneauSerializer(panneau, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)

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
        current_year = datetime.now().year

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
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi de cette semaine
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche de cette semaine

    # Récupérer les données de consommation par jour de la semaine
    data = (
        PanneauData.objects.filter(
            panneau__module_id=module_id,
            date__gte=start_of_week,
            date__lte=end_of_week,
        )
        .values("date__weekday")
        .annotate(total_consumption=Sum("consumption"))
        .order_by("date__weekday")
    )

    # Organiser les données pour correspondre aux jours de la semaine (lundi, mardi, etc.)
    week_labels = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    consumption_data = {label: 0 for label in week_labels}

    for entry in data:
        day_of_week = entry["date__weekday"]
        consumption_data[week_labels[day_of_week]] = entry["total_consumption"]

    return Response(consumption_data)