from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from fish.models import FishingPond
import uuid
from datetime import datetime
import pytz


class CustomUser(AbstractUser):
    userName = models.CharField(max_length=100, unique=True)
    userId = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="唯一标识符"
    )
    userKey = models.CharField(max_length=255, unique=True)
    openId = models.CharField(max_length=100, unique=True)
    phoneNumber = models.CharField(max_length=100, blank=True, unique=True)

    class Meta:
        db_table = "user_management"
        verbose_name = "用户表"
        verbose_name_plural = "用户表"

    def __str__(self):
        return self.username

    @classmethod
    def create_or_update_from_wechat(cls, user_data):
        """
        从微信数据创建或更新用户实例。

        :param user_data: 包含微信返回的用户数据的字典
        :return: 创建或更新后的用户实例
        """
        # 解析微信返回的数据
        userName = user_data.get("username")
        userKey = user_data.get("openId")
        openId = user_data.get("openId")
        phoneNumber = user_data.get("phoneNumber")

        # 尝试根据 openId 查找现有用户
        user, created = cls.objects.update_or_create(
            openId=openId,
            defaults={
                "userName": userName,
                "userId": uuid.uuid4(),
                "openId": openId,
                "userKey": userKey,
                "phoneNumber": phoneNumber,
                "is_superuser": False,
                "username": userName,
                "first_name": "Anonymous",
                "last_name": "Anonymous",
                "email": "@email",
                "date_joined": datetime.now(pytz.timezone("Asia/Shanghai")),
                "is_active": True,
                "is_staff": True,
                "password": userKey,
            },
        )

        return user


class FavoriteFishingPond(models.Model):
    # 用户（外键引用 CustomUser 模型）
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="favorite_ponds",
        verbose_name="用户",
    )

    # 鱼塘（外键引用 FishingPond 模型）
    fishing_pond = models.ForeignKey(
        FishingPond,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="鱼塘",
    )

    # 收藏时间（自动设置为当前时间）
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        db_table = "favorite_fishing_pond"
        verbose_name = "用户收藏鱼塘"
        verbose_name_plural = "用户收藏鱼塘"
        unique_together = ("user", "fishing_pond")  # 确保用户对同一鱼塘只能收藏一次
