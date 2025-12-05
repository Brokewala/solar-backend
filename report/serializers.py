# from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

# models
from .models import Report
from .models import ReportComment
from .models import ReportState
from users.serializers import ProfilUserSerializer


class ReportSerializer(serializers.ModelSerializer):
    user = ProfilUserSerializer(many=False, read_only=True)

    class Meta:
        model = Report
        fields = "__all__"


class ReportCommentSerializer(serializers.ModelSerializer):
    sender = ProfilUserSerializer(many=False, read_only=True)
    report = ReportSerializer(many=False, read_only=True)

    class Meta:
        model = ReportComment
        fields = "__all__"


class ReportStateSerializer(serializers.ModelSerializer):
    report = ReportSerializer(many=False, read_only=True)

    class Meta:
        model = ReportState
        fields = "__all__"
