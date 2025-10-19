from rest_framework.routers import DefaultRouter
from .views import RegisterView, CustomTokenObtainPairView, whoami, UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path, include

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", whoami, name="whoami"),
    path("", include(router.urls)),
]
