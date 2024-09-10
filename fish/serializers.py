# serializers.py
from rest_framework import serializers
from .models import FishingPond


class FishingPondSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = FishingPond
        fields = "__all__"

    def get_latitude(self, obj):
        if obj.location:
            return obj.location.y  # 经度
        return None

    def get_longitude(self, obj):
        if obj.location:
            return obj.location.x  # 纬度
        return None
