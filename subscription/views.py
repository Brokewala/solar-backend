from rest_framework import status

# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404

# models
from users.models import ProfilUser
from .models import Subscription
from .models import SubscriptionPrice

# serializer
from .serializers import SubscriptionSerializer
from .serializers import SubscriptionPriceSerializer


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_Subscription(request):
    sub_data = Subscription.objects.all().order_by("-createdAt")
    serializer = SubscriptionSerializer(sub_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_subscription_by_user(request, user_id):
    sud_data = Subscription.objects.get(user__id=user_id)
    serializer = SubscriptionSerializer(sud_data, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Subscription APIView
class SubscriptionAPIView(APIView):

    def get_object(self, sub_id):
        try:
            return Subscription.objects.get(id=sub_id)
        except Subscription.DoesNotExist:
            return Response(
                {"error": "Subscription not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        user_id = request.data.get("user_id")
        stockage_ensuel = request.data.get("stockage_ensuel")
        assistance = request.data.get("assistance")
        entretien = request.data.get("entretien")
        monitoring = request.data.get("monitoring")
        remote_control = request.data.get("remote_control")
        planing = request.data.get("planing")
        alert = request.data.get("alert")
        name = request.data.get("name")

        if user_id is None or name is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

        # get user
        user_data = get_object_or_404(ProfilUser, id=user_id)

        # create Subscription
        sub_data = Subscription.objects.create(
            name=name,
            user=user_data,
        )
        # save into database
        sub_data.save()

        if stockage_ensuel:
            sub_data.stockage_ensuel = stockage_ensuel

        if assistance:
            sub_data.assistance = assistance

        if entretien:
            sub_data.entretien = entretien

        if monitoring:
            sub_data.monitoring = monitoring

        if remote_control:
            sub_data.remote_control = remote_control

        if planing:
            sub_data.planing = planing

        if alert:
            sub_data.alert = alert

        sub_data.save()

        serializer = SubscriptionSerializer(sub_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, sub_id):
        sub_data = self.get_object(sub_id=sub_id)
        serializer = SubscriptionSerializer(sub_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, sub_id):
        sub_data = self.get_object(sub_id=sub_id)
        # variables
        stockage_ensuel = request.data.get("stockage_ensuel")
        assistance = request.data.get("assistance")
        entretien = request.data.get("entretien")
        monitoring = request.data.get("monitoring")
        remote_control = request.data.get("remote_control")
        planing = request.data.get("planing")
        alert = request.data.get("alert")
        name = request.data.get("name")

        #  name
        if name:
            sub_data.name = name

        if stockage_ensuel:
            sub_data.stockage_ensuel = stockage_ensuel

        if assistance:
            sub_data.assistance = assistance

        if entretien:
            sub_data.entretien = entretien

        if monitoring:
            sub_data.monitoring = monitoring

        if remote_control:
            sub_data.remote_control = remote_control

        if planing:
            sub_data.planing = planing

        if alert:
            sub_data.alert = alert

        sub_data.save()

        serializer = SubscriptionSerializer(sub_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, sub_id):
        sub_data = self.get_object(sub_id=sub_id)
        sub_data.delete()
        return Response(
            {"message": "Subscription is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# SubscriptionPrice
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_SubscriptionPrice_by_subscription(request, sub_id):
    sub_data = SubscriptionPrice.objects.filter(subscription__id=sub_id)
    serializer = SubscriptionPriceSerializer(sub_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# SubscriptionPrice
class SubscriptionPriceAPIView(APIView):

    def get_object(self, sub_id):
        try:
            return SubscriptionPrice.objects.get(id=sub_id)
        except SubscriptionPrice.DoesNotExist:
            return Response(
                {"error": "Subscription Price Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        price = request.data.get("price")
        subscription_type = request.data.get("subscription_type")
        sub_id = request.data.get("sub_id")

        if (
            price is None
            or subscription_type is None
            or sub_id is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get 
        sub_data = get_object_or_404(Subscription, id=sub_id)

        sub_data = SubscriptionPrice.objects.create(
            price=price,
            subscription=sub_data,
            subscription_type=subscription_type,
        )
        # save into database
        sub_data.save()
        serializer = SubscriptionPriceSerializer(sub_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, sub_id):
        sub_data = self.get_object(sub_id=sub_id)
        serializer = SubscriptionPriceSerializer(sub_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, sub_id):
        sub_data = self.get_object(sub_id=sub_id)
        # variables
        price = request.data.get("price")
        subscription_type = request.data.get("subscription_type")

        if price:
            sub_data.price = price

        if subscription_type:
            sub_data.subscription_type = subscription_type

        sub_data.save()
        serializer = SubscriptionPriceSerializer(sub_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, sub_id):
        sub_data = self.get_object(sub_id=sub_id)
        sub_data.delete()
        return Response(
            {"message": "Subscription price is deleted"}, status=status.HTTP_204_NO_CONTENT
        )
