from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from users.views import (
    CreateUserView,
    ManageUserView
)

app_name = "users"

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token-pair-obtain"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("register/", CreateUserView.as_view(), name="register"),
    path("me/", ManageUserView.as_view(), name="manage")
]
