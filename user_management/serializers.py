from rest_framework import serializers
from .models import FavoriteFishingPond, CustomUser, FishingPond


class FavoriteFishingPondSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteFishingPond
        fields = ["user", "fishing_pond"]
