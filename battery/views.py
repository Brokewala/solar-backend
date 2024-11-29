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


# django
from datetime import timedelta
from datetime import datetime
from django.db.models import Sum, F
from django.db.models.functions import Coalesce


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


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_battery(request):
    batttery = Battery.objects.all().order_by("-createdAt")
    serializer = BatteryAllSerializer(batttery, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_battery_by_module(request, module_id):
    battery = Battery.objects.filter(module__id=module_id)
    serializer = BatterySerializer(battery, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


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

    def get(self, request, battery_id):
        battery = self.get_object(battery_id=battery_id)
        serializer = BatterySerializer(battery, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, battery_id):
        battery = self.get_object(battery_id=battery_id)
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

    def delete(self, request, battery_id):
        battery = self.get_object(battery_id=battery_id)
        battery.delete()
        return Response(
            {"message": "battery is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# get all BatteryData
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

    def post(self, request):
        tension = request.data.get("tension")
        puissance = request.data.get("puissance")
        courant = request.data.get("courant")
        energy = request.data.get("energy")
        pourcentage = request.data.get("pourcentage")
        battery_id = request.data.get("battery_id")

        if (
            tension is None
            or puissance is None
            or courant is None
            or energy is None
            or pourcentage is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get battery
        battery = get_object_or_404(Battery, id=battery_id)

        battery_data = BatteryData.objects.create(
            tension=tension,
            battery=battery,
            puissance=puissance,
            courant=courant,
            energy=energy,
            pourcentage=pourcentage,
        )
        # save into database
        battery_data.save()
        serializer = BatteryDataSerializer(battery_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, battery_data_id):
        module = self.get_object(battery_data_id=battery_data_id)
        serializer = BatteryDataSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, battery_data_id):
        battery_data = self.get_object(battery_data_id=battery_data_id)
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

    def delete(self, request, battery_data_id):
        battery = self.get_object(battery_data_id=battery_data_id)
        battery.delete()
        return Response(
            {"message": "battery data is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# get all BatteryPlanning
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_batteryplanning_by_battery(request, battery_id):
    battery_data = BatteryPlanning.objects.filter(battery__id=battery_id)
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

        if (
            energie is None
            or date_debut is None
            or date_fin is None
            or done is None
            or battery_id is None
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
    battery_data = BatteryRelaiState.objects.filter(battery__id=battery_id)
    serializer = BatteryRelaiStateSerializer(battery_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


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
# getDureeUtilisationBatterieAnuelleByIdModule
@api_view(["GET"])
def get_duree_utilisation_batterie_annuelle_by_id_module(request, module_id):
    """
    Endpoint DRF pour obtenir la durée totale d'utilisation des batteries
    associées à un module spécifique pour l'année en cours.

    :param request: Objet de requête
    :param module_id: ID du module (passé dans l'URL)
    :return: JSON contenant la durée totale en heures ou un message d'erreur
    """
    try:
        # Vérifier si le module existe
        module = Modules.objects.get(id=module_id)

        # Récupérer l'année en cours
        current_year = datetime.now().year

        # Récupérer les batteries associées au module
        plannings = BatteryPlanning.objects.filter(
            battery__module=module,
            date_debut__year=current_year,
            date_fin__year=current_year,
        )

        # Calculer la durée totale d'utilisation en heures
        total_duration = 0
        for planning in plannings:
            if planning.date_debut and planning.date_fin:
                duration = (planning.date_fin - planning.date_debut).total_seconds() / 3600  # Conversion en heures
                total_duration += duration

        return Response(
            {"duree_annuelle": round(total_duration, 2)},  # Retourner avec 2 décimales
            status=status.HTTP_200_OK,
        )

    except Modules.DoesNotExist:
        return Response(
            {"error": "Le module avec l'ID spécifié n'existe pas."},
            status=status.HTTP_404_NOT_FOUND,
        )


# getCouleurBatterieByIdModule
@api_view(["GET"])
def get_couleur_batterie_by_id_module(request, module_id):
    """
    Endpoint DRF pour obtenir les couleurs des batteries associées à un module spécifique.

    :param request: Objet de requête
    :param module_id: ID du module (passé dans l'URL)
    :return: JSON contenant les couleurs des batteries ou un message d'erreur
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

# listeBatterieDataByDateAndIdModule
@api_view(["GET"])
def liste_batterie_data_by_date_and_id_module(request, module_id,date):
    """
    Endpoint DRF pour récupérer les données BatteryData associées à un module spécifique,
    filtrées par une plage de dates.

    :param request: Objet de requête
    :param module_id: ID du module (passé dans l'URL)
    :queryparam start_date: Date de début (format 'YYYY-MM-DD')
    :queryparam end_date: Date de fin (format 'YYYY-MM-DD')
    :return: JSON des BatteryData ou message d'erreur
    """
    # start_date = request.query_params.get("start_date")
    # end_date = request.query_params.get("end_date")

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

        # Récupérer les batteries associées au module
        batteries = module.modules_battery.all()

        # Filtrer les BatteryData par batteries et plage de dates
        battery_data = BatteryData.objects.filter(
            battery__in=batteries,
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


# listeDureeBatterieMensuelleByIdModuleAndMonth
@api_view(["GET"])
def liste_duree_batterie_mensuelle_by_id_module_and_month(request, module_id, month):
    """
    Récupère la durée d'utilisation mensuelle des batteries d'un module pour un mois donné.
    """
    try:
        # Vérifier si le module existe
        batteries = Battery.objects.filter(module_id=module_id)
        if not batteries.exists():
            return Response(
                {"error": "Le module avec l'ID spécifié n'a pas de batteries associées."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Valider et convertir le mois
        try:
            # Vérification du format attendu pour 'month' : 'YYYY-MM'
            date_filter = datetime.strptime(month, "%Y-%m")
        except ValueError:
            return Response(
                {"error": "Le format du mois est incorrect. Utilisez 'YYYY-MM'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filtrer les données BatteryData pour le mois donné
        data = BatteryData.objects.filter(
            battery__in=batteries,
            createdAt__year=date_filter.year,
            createdAt__month=date_filter.month,
        )

        # Calculer la durée totale (somme des valeurs pertinentes)
        total_duration = sum(float(item.energy or 0) for item in data)

        # Retourner la durée totale et les détails
        return Response(
            {
                "module_id": module_id,
                "month": month,
                "total_duration": total_duration,
                "details": [{"battery_id": d.battery.id, "energy": d.energy} for d in data],
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Une erreur s'est produite.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )