from django.urls import path
from .views import GetFish

app_name = "fish"
urlpatterns = [
    path("getFish/", GetFish.as_view(), name="getFish"),
]
