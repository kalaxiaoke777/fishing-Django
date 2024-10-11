from django.urls import path
from .views import (
    UserLoginView,
    LogoutView,
    WeChatLoginCallbackView,
    WeChatLoginRegister,
    FavoriteFishing,
    UpdateUser,
)

app_name = "user_management"
urlpatterns = [
    path("login/", UserLoginView.as_view(), name="user_login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "wechat/callback/",
        WeChatLoginCallbackView.as_view(),
        name="wechat_login_callback",
    ),
    path(
        "wechat/register/",
        WeChatLoginRegister.as_view(),
        name="wechat_login_register",
    ),
    path(
        "favoriteFishing/",
        FavoriteFishing.as_view(),
        name="favoriteFishing",
    ),
    path(
        "updateUser/",
        UpdateUser.as_view(),
        name="updateUser",
    ),
]
