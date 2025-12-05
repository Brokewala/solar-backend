from rest_framework import serializers


class WeekRangeSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()


class WeeklyBucketSerializer(serializers.Serializer):
    week = serializers.IntegerField()
    range = WeekRangeSerializer()
    days = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    totals = serializers.DictField(child=serializers.FloatField())


class WeeklyByMonthResponseSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    entity = serializers.CharField()
    module_id = serializers.CharField()
    field = serializers.CharField()
    weeks = WeeklyBucketSerializer(many=True)
