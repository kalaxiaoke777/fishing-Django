import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
from datetime import timedelta
from urllib.parse import quote
from django.contrib.auth import login, logout as django_logout
from django.utils import timezone
from .models import FishingPond
from user_management.models import FavoriteFishingPond, CustomUser
from rest_framework.permissions import AllowAny
from .serializers import FishingPondSerializer, FishingPondSearchSerializer


class GetFish(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user_id = request.GET.get("openid")
            is_public = request.GET.get("isPublic")
            isFavorite = request.GET.get("isFavorite")
            if is_public == "1":
                fish_pond = FishingPond.objects.filter(is_public=True)
            else:
                fish_pond = FishingPond.objects.filter(is_public=False, user_id=user_id)
            if isFavorite:
                if not user_id:
                    raise Exception("openid is None")
                # 获取用户对象
                _user_id_obj = CustomUser.objects.get(openId=user_id)
                _user_id = _user_id_obj.id

                # 获取用户喜欢的所有钓鱼池 ID
                favorite_fish_pond_ids = FavoriteFishingPond.objects.filter(
                    user_id=_user_id
                ).values_list("fishing_pond_id", flat=True)

                # 查找对应的钓鱼池记录
                fish_pond = FishingPond.objects.filter(
                    pond_id__in=favorite_fish_pond_ids
                )
            serializer = FishingPondSerializer(fish_pond, many=True)
            return Response(
                {
                    "success": False,
                    "code": 200,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "data": [], "msg": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SearchFish(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user_id = request.GET.get("id")
            is_public = request.GET.get("isPublic")
            if is_public == "1" or is_public == 1:
                fish_pond = FishingPond.objects.filter(is_public=True)
            else:
                fish_pond = FishingPond.objects.filter(is_public=False, user_id=user_id)
            serializer = FishingPondSearchSerializer(fish_pond, many=True)
            return Response(
                {
                    "code": 200,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
