from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Account
from accounts.serializers import (
    InputAccountRegisterSerializer,
    OutputAccountSerializer,
)


class RegisterAccountAPIView(APIView):
    @swagger_auto_schema(
        request_body=InputAccountRegisterSerializer(),
        responses={
            200: 'Empty',
        }
    )
    def post(self, request):
        serializer = InputAccountRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        if not Account.objects \
                .filter(username=username) \
                .exists():  # todo: change register
            Account.objects.create_user(
                username=username,
                password=serializer.validated_data['password'],
            )
        else:
            raise ValidationError(f"User with username {username}.")

        return Response(status=status.HTTP_201_CREATED)


class AccountSelfAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get current account information",
        responses={200: OutputAccountSerializer()},
    )
    def get(self, request):
        user = request.user
        data = OutputAccountSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)


class AccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get information about user",
        operation_description="Could returns 404 if user is not a friend!",
        responses={200: OutputAccountSerializer()},
    )
    def get(self, request, pk):
        current_user: Account = request.user
        if current_user.id == pk:
            user = current_user
        else:
            user = get_object_or_404(current_user.friends.all(), pk=pk)
        data = OutputAccountSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)
