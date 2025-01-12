from rest_framework.serializers import ModelSerializer

# model
from .models import Notification


# serializer
class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


