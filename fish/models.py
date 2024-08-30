from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class FishingPond(models.Model):
    # 鱼塘ID（唯一标识）
    pond_id = models.AutoField(primary_key=True, verbose_name="鱼塘ID")

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="唯一标识符"
    )
    # 鱼塘名称（必填）
    name = models.CharField(max_length=255, unique=True, verbose_name="鱼塘名称")

    # 鱼塘简介（非必填）
    description = models.TextField(blank=True, verbose_name="鱼塘简介")

    # 鱼塘评分（必填），可以使用0到10之间的评分
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="鱼塘评分",
    )

    # 鱼塘价格（非必填）
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="鱼塘价格"
    )

    # 鱼塘类型（四种类型：野塘、黑坑、天然、欢乐，必填）
    POND_TYPE_CHOICES = [
        ("wild", "野塘"),
        ("black_pit", "黑坑"),
        ("natural", "天然"),
        ("happy", "欢乐"),
    ]
    pond_type = models.CharField(
        max_length=20, choices=POND_TYPE_CHOICES, verbose_name="鱼塘类型"
    )

    image_base64 = models.TextField(
        verbose_name="鱼塘图片 (Base64编码)", blank=True, null=True
    )

    # 鱼塘电话（非必填）
    phone_number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="鱼塘电话"
    )

    # 营业开始时间（非必填）
    opening_time = models.TimeField(blank=True, null=True, verbose_name="营业开始时间")

    # 营业结束时间（非必填）
    closing_time = models.TimeField(blank=True, null=True, verbose_name="营业结束时间")

    # 鱼种类（是个数组，非必填）
    fish_species = ArrayField(
        models.CharField(max_length=100), blank=True, null=True, verbose_name="鱼种类"
    )

    # 鱼塘位置（PostGIS的点字段，必填）
    location = models.PointField(srid=4326, verbose_name="鱼塘位置")

    class Meta:
        db_table = "fishing_pond"
        verbose_name = "鱼塘"
        verbose_name_plural = "鱼塘"
        indexes = [
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return self.name
