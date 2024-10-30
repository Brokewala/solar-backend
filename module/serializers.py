# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
# model
from .models import Modules, ModulesInfo, ModulesDetail
from users.serializers import ProfilUserSerializer


# serializer
class ModulesSerializer(serializers.ModelSerializer):
    user = ProfilUserSerializer(many=False, read_only=True)
    class Meta:
        model = Modules
        fields = "__all__"

# ModulesInfo
class ModulesInfoSerializer(serializers.ModelSerializer):
    module = ModulesSerializer(many=False, read_only=True)
    class Meta:
        model = ModulesInfo
        fields = "__all__"

# ModulesDetail
class ModulesDetailSerializer(serializers.ModelSerializer):
    module_info = ModulesInfoSerializer(many=False, read_only=True)
    class Meta:
        model = ModulesDetail
        fields = "__all__"
