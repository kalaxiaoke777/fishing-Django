from django.urls import path
from .views import GetFish, SearchFish

app_name = "fish"
urlpatterns = [
    path("getFish/", GetFish.as_view(), name="getFish"),
    path("searchFish/", SearchFish.as_view(), name="getFish"),
]
