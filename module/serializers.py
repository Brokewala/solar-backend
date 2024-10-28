from rest_framework.serializers import ModelSerializer

# model
from .models import Subscription


# serializer
class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


