from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "user_management/", include("user_management.urls", namespace="user_management")
    ),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
