import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from datetime import timedelta
from urllib.parse import quote
from django.contrib.auth import login, logout as django_logout
from django.utils import timezone
from .models import FishingPond
from user_management.models import FavoriteFishingPond, CustomUser
from rest_framework.permissions import AllowAny
from .serializers import FishingPondSerializer, FishingPondSearchSerializer
from django.db.models import Q


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
            serializer = FishingPondSerializer(
                fish_pond, many=True, context={"request": request}
            )
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
            # 获取请求参数
            name = request.GET.get("name", "").strip()
            user_id = request.GET.get("id")

            # 如果name为空，直接返回空结果
            if not name:
                return Response(
                    {
                        "success": True,
                        "code": 200,
                        "data": [],
                    },
                    status=status.HTTP_200_OK,
                )

            # 基础查询集
            query = Q()

            # 添加模糊查询条件
            if name:
                query &= Q(name__icontains=name)

            query &= Q(is_public=True) | Q(is_public=False, user_id=user_id)

            # 执行查询
            fish_pond = FishingPond.objects.filter(query)

            # 序列化结果
            serializer = FishingPondSearchSerializer(fish_pond, many=True)

            return Response(
                {
                    "success": True,
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
