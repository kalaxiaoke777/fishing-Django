from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from fish.models import FishingPond


class CustomUser(AbstractUser):
    # 你可以添加额外的字段
    id = models.BigIntegerField(primary_key=True, verbose_name="ID")
    userName = models.CharField(max_length=100, unique=True)
    userId = models.CharField(max_length=100, unique=True)
    userKey = models.CharField(max_length=255, unique=True)
    openId = models.CharField(max_length=100, unique=True)
    phoneNumber = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "user_management"
        verbose_name = "用户表"
        verbose_name_plural = "用户表"

    def __str__(self):
        return self.username


class FavoriteFishingPond(models.Model):
    # 用户（外键引用 User 模型）
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_fishing_ponds",
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
