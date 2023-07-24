from django.urls import path, include
from rest_framework import routers

from user.views import UserViewSet, CreateUserView, ManageUserView

app_name = "user"
router = routers.DefaultRouter()
router.register("passengers", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", CreateUserView.as_view(), name="create"),
    path("me/", ManageUserView.as_view(), name="manage"),
]
