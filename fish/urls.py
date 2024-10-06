from django.urls import path
from .views import GetFish, SearchFish, GetFishList, AddFish, GetFishSingle

app_name = "fish"
urlpatterns = [
    path("getFish/", GetFish.as_view(), name="getFish"),
    path("getFishSingle/", GetFishSingle.as_view(), name="getFishSingle"),
    path("searchFish/", SearchFish.as_view(), name="getFish"),
    path("getFishList/", GetFishList.as_view(), name="getFishList"),
    path("addFish/", AddFish.as_view(), name="addFish"),
]
