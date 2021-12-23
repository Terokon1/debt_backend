from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.serializers import (
    OutputTokenObtainPairSerializer,
    OutputTokenRefreshSerializer,
    OutputTokenVerifySerializer,
)


class DecoratedTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        responses={
            200: OutputTokenObtainPairSerializer()
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DecoratedTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        responses={
            200: OutputTokenRefreshSerializer()
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DecoratedTokenVerifyView(TokenVerifyView):
    @swagger_auto_schema(
        responses={
            200: OutputTokenVerifySerializer(),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
