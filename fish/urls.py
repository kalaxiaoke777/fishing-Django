from django.urls import path
from .views import GetFish, SearchFish, GetFishList

app_name = "fish"
urlpatterns = [
    path("getFish/", GetFish.as_view(), name="getFish"),
    path("searchFish/", SearchFish.as_view(), name="getFish"),
    path("getFishList/", GetFishList.as_view(), name="getFishList"),
]
