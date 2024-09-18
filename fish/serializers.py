# serializers.py
from rest_framework import serializers
from .models import FishingPond
from user_management.models import CustomUser, FavoriteFishingPond


class FishingPondSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = FishingPond
        fields = "__all__"

    def get_latitude(self, obj):
        if obj.location:
            return obj.location.y
        return None

    def get_longitude(self, obj):
        if obj.location:
            return obj.location.x
        return None

    def get_is_favorite(self, obj):
        request = self.context.get("request")
        if request and request.GET.get("openid"):
            user_openid = request.GET.get("openid")
            try:
                user = CustomUser.objects.get(openId=user_openid)
                user_id = user.id
                # 检查当前钓鱼池是否在用户的收藏中
                return FavoriteFishingPond.objects.filter(
                    user_id=user_id, fishing_pond_id=obj.pond_id
                ).exists()
            except CustomUser.DoesNotExist:
                return False
        return False


class FishingPondSearchSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = FishingPond
        fields = ["name", "id", "distance", "latitude", "longitude", "is_public"]

    def get_id(self, obj):
        return obj.pond_id

    def get_distance(self, obj):
        return 12

    def get_latitude(self, obj):
        if obj.location:
            return obj.location.y
        return None

    def get_longitude(self, obj):
        if obj.location:
            return obj.location.x
        return None
