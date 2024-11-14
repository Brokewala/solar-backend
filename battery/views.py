from rest_framework import status

# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404


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
    battery = Battery.objects.get(module__id=module_id)
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
