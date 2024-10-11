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
from .serializers import (
    FishingPondSerializer,
    FishingPondSingleSerializer,
    FishingPondSearchSerializer,
)
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.contrib.gis.geos import Point


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


class GetFishSingle(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user_id = request.GET.get("user_id")
            is_public = bool(request.GET.get("is_public"))
            id = request.GET.get("id")
            if is_public:
                fish_pond = FishingPond.objects.get(uuid=id)
            else:
                fish_pond = FishingPond.objects.get(
                    is_public=False, user_id=user_id, uuid=id
                )
            serializer = FishingPondSingleSerializer(
                fish_pond, context={"request": request}
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
            onloadLocation = json.loads(request.GET.get("onloadLocation"))

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
            serializer = FishingPondSearchSerializer(
                fish_pond, many=True, context={"request": request}
            )

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


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # 默认每页返回10个结果
    page_size_query_param = "page_size"  # 允许用户自定义每页的大小
    max_page_size = 100  # 允许的最大每页大小


class GetFishList(APIView):
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
                fish_pond = FishingPond.filter(pond_id__in=favorite_fish_pond_ids)

            # 初始化分页
            paginator = StandardResultsSetPagination()
            paginated_fish_pond = paginator.paginate_queryset(fish_pond, request)

            # 序列化数据
            serializer = FishingPondSerializer(
                paginated_fish_pond, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(
                {"success": False, "data": [], "msg": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AddFish(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            location_data = request.data.get("location", {})
            location = None
            if location_data and "coordinates" in location_data:
                coordinates = location_data["coordinates"]
                location = Point(coordinates[0], coordinates[1])
            else:
                raise Exception("Invalid location data")
            if request.data.get("is_public", "") is False:
                if request.data.get("user_id") == "":
                    raise Exception("user_id is required when is_public is True")
            fish = FishingPond.objects.create(
                uuid=request.data.get("uuid", ""),
                name=request.data.get("title", ""),
                description=request.data.get("description", ""),
                rating=request.data.get("rating", ""),
                price=request.data.get("price", ""),
                pond_type=request.data.get("pond_type", ""),
                image_base64=request.data.get("image_base64", ""),
                phone_number=request.data.get("phone_number", ""),
                opening_time=request.data.get("opening_time", ""),
                closing_time=request.data.get("closing_time", ""),
                fish_species=request.data.get("fish_species", ""),
                is_public=request.data.get("is_public", ""),
                user_id=request.data.get("user_id", ""),
                location=location,
            )
            fish.save()
            return Response(
                {
                    "success": True,
                    "code": 200,
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "data": [], "msg": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
