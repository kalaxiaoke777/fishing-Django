# serializers.py
import json
from rest_framework import serializers
from .models import FishingPond
from user_management.models import CustomUser, FavoriteFishingPond
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance


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


class FishingPondSingleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FishingPond
        fields = "__all__"


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
        # 假设前端传来的坐标以查询参数的形式给出，例如 ?lat=40.7128&lon=-74.0060
        locatiosns = json.loads(self.context["request"].GET.get("onloadLocation"))

        if locatiosns[1] and locatiosns[0]:
            # 创建一个Point对象表示前端传来的坐标
            user_location = Point(
                float(locatiosns[0]), float(locatiosns[1]), srid=4326
            )  # 假设使用WGS84坐标系
            # 假设FishingPond模型中的location字段是地理位置字段
            distance = user_location.distance(obj.location)
            # 可以根据需要转换距离单位，例如转换为米或千米
            return round(distance * 100, 1)
        else:
            # 如果没有提供坐标，则返回None或适当的默认值
            return None

    def get_latitude(self, obj):
        if obj.location:
            return obj.location.y
        return None

    def get_longitude(self, obj):
        if obj.location:
            return obj.location.x
        return None
