from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


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


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    # product = models.ForeignKey(
    #     Product, on_delete=models.CASCADE, related_name="favorited_by"
    # )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "favorite"
        verbose_name = "收藏"
        verbose_name_plural = "收藏"
        unique_together = ("user", "product")  # 确保每个用户对每个商品只能收藏一次

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.product.name}"
