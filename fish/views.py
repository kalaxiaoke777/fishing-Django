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
from rest_framework.permissions import AllowAny
from .serializers import FishingPondSerializer


class GetFish(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user_id = request.GET.get("id")
            is_public = request.GET.get("isPublic")
            if is_public == "1":
                fish_pond = FishingPond.objects.filter(is_public=True)
            else:
                fish_pond = FishingPond.objects.filter(is_public=False, user_id=user_id)
            serializer = FishingPondSerializer(fish_pond, many=True)
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
