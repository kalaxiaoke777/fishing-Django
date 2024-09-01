from django.utils import timezone
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token


class TokenExpirationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 仅对需要验证 token 的路径进行验证
        if request.path.startswith("/api/"):
            # 获取请求中的 token（假设在请求的 Authorization 头中）
            token_key = request.headers.get("Authorization")
            if token_key:
                # 去除 "Token " 前缀
                token_key = token_key.replace("Token ", "")
                try:
                    token = Token.objects.get(key=token_key)
                    # 假设 token 的过期时间存储在 `expires_at` 字段中
                    expires_at = (
                        token.user.profile.expires_at
                    )  # 这里假设用户模型有 `profile` 外键，`profile` 中有 `expires_at` 字段
                    if timezone.now() > expires_at:
                        return JsonResponse({"detail": "Token expired."}, status=401)
                except Token.DoesNotExist:
                    return JsonResponse({"detail": "Invalid token."}, status=401)
            else:
                return JsonResponse({"detail": "Token missing."}, status=401)
        return None

    def process_response(self, request, response):
        return response
