from rest_framework import status

# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404


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
    prise = Prise.objects.get(module__id=module_id)
    serializer = PriseSerializer(prise, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)

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
        done = request.data.get("done")
        prise_id = request.data.get("prise_id")

        if (
            consomation is None
            or date_debut is None
            or date_fin is None
            or done is None
            or prise_id is None
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
    prise_data = PriseRelaiState.objects.filter(prise__id=prise_id)
    serializer = PriseRelaiStateSerializer(prise_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


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
