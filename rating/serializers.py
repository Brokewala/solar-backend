# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

# model
from .models import Rating
from users.serializers import ProfilUserSerializer


# serializer
class RatingSerializer(serializers.ModelSerializer):
    user = ProfilUserSerializer(many=False, read_only=True)
    class Meta:
        model = Rating
        fields = "__all__"
