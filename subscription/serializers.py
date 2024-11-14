from rest_framework.serializers import ModelSerializer

# model
from .models import Subscription,SubscriptionPrice


# serializer
class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"



class SubscriptionPriceSerializer(ModelSerializer):
    subscription = SubscriptionSerializer(many=False, read_only=True)

    class Meta:
        model = SubscriptionPrice
        fields = "__all__"

