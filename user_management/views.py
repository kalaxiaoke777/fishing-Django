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
from .models import CustomUser, FavoriteFishingPond
from fish.models import FishingPond
from .serializers import FavoriteFishingPondSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.models import Token


class FavoriteFishing(APIView):

    def get(self, request, format=None):
        return Response(status=405)

    def post(self, request, *args, **kwargs):
        user_id = request.GET.get("user")
        fishing_pond_id = request.GET.get("fishing_pond")
        favortite = request.GET.get("favortite")

        try:
            user = CustomUser.objects.get(openId=user_id)
            fishing_pond = FishingPond.objects.get(pond_id=fishing_pond_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"success": False, "data": [], "msg": "none"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except FishingPond.DoesNotExist:
            return Response(
                {"success": False, "data": [], "msg": "none"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查用户是否已经收藏过该鱼塘
        if FavoriteFishingPond.objects.filter(
            user=user, fishing_pond=fishing_pond
        ).exists():
            return Response(
                {"success": False, "data": [], "msg": "用户一已收藏"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 创建新的收藏记录
        favorite = FavoriteFishingPond.objects.create(
            user=user, fishing_pond=fishing_pond
        )

        serializer = FavoriteFishingPondSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        try:
            code = request.GET.get("code")
            if not code:
                return Response(
                    {"error": "Missing code parameter"},
                    status=status.HTTP_400_BAD_REQUEST,
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
            # 判断openid是否存在
            if CustomUser.objects.filter(openId=openid).exists():
                user = CustomUser.objects.get(openId=openid)
                token, created = Token.objects.get_or_create(user=user)
                # 登录用户
                backend = "django.contrib.auth.backends.ModelBackend"
                user.backend = backend
                login(request, user, backend=backend)
                return Response(
                    {
                        "openid": openid,
                        "session_key": access_token,
                        "userName": user.username,
                        "phoneNumber": user.phoneNumber,
                        "token": token.key,
                        "code": 200,
                    }
                )
            else:
                return Response(
                    {
                        "openid": openid,
                        "session_key": access_token,
                        "code": 50001,
                        "userName": "",
                        "phoneNumber": "",
                    }
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WeChatLoginRegister(APIView):

    def post(self, request):
        try:
            data = json.loads(request.body)

            # 假设 create_or_update_from_wechat 方法会根据微信的数据创建或更新用户
            user = CustomUser.create_or_update_from_wechat(data)
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            return Response(
                {
                    "message": "注册成功",
                    "data": [],
                    "code": 200,
                }
            )
        except Exception as e:
            return Response(
                {"message": str(e), "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateUser(APIView):
    """
    @summary: 更新用户信息
    need: openid
    user_name: 用户名
    phone_number: 手机号
    """

    def post(self, request):
        try:
            openid = request.GET.get("openid")
            user_name = request.GET.get("user_name")
            phone_number = request.GET.get("phone_number")

            if CustomUser.objects.filter(openId=openid).exists():
                user = CustomUser.objects.get(openId=openid)
                user.user_name = user_name
                user.phone_number = phone_number
                user.save()
                return Response(
                    {
                        "message": "修改成功",
                        "data": {
                            "user_name": user_name,
                            "phone_number": phone_number,
                        },
                        "code": 200,
                    }
                )
            else:
                raise Exception("用户不存在")

        except Exception as e:
            return Response(
                {"message": str(e), "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
