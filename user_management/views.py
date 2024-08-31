import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
from urllib.parse import quote
from django.contrib.auth import login, logout as django_logout
from django.utils import timezone
from .models import CustomUser
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        appid = settings.WECHAT_APPID
        redirect_uri = quote(settings.WECHAT_REDIRECT_URI)
        url = f"https://open.weixin.qq.com/connect/qrconnect?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_login&state=STATE#wechat_redirect"
        return Response({"redirect_url": url}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        django_logout(request)
        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )


class WeChatLoginCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        if not code:
            return Response(
                {"error": "Missing code parameter"}, status=status.HTTP_400_BAD_REQUEST
            )

        appid = settings.WECHAT_APPID
        secret = settings.WECHAT_SECRET
        # url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code"
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code"
        response = requests.get(url)
        data = response.json()

        access_token = data.get("session_key")
        openid = data.get("openid")

        if not access_token or not openid:
            return Response(
                {"error": "Failed to get access token or openid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"openid": openid, "session_key": access_token})


class WeChatLoginRegister(APIView):
    def post(self, request):
        data = json.loads(request.body)
        # 创建或更新用户
        user = CustomUser.create_or_update_from_wechat(data)
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        # 选择认证后端
        backend = "django.contrib.auth.backends.ModelBackend"
        user.backend = backend
        login(request, user, backend=backend)
