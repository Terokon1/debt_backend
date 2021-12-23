from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import selectors, errors
from accounts.models import Account
from accounts.serializers import (
    OutputFriendRequestSerializer,
    InputFriendRequestSerializer,
    InputFriendRequestUpdateSerializer,
)
from accounts.services import CreateFriendRequestService, UpdateFriendRequestService


class FriendRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List of friends' requests to accept",
        tags=["friend requests"],
        responses={200: OutputFriendRequestSerializer(many=True)},
    )
    def get(self, request):
        friend_requests = selectors.get_friend_requests_to_accept(request.user)

        serializer = OutputFriendRequestSerializer(friend_requests, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create friend request",
        operation_description="""
Some of friend requests could not be created but `201` status code will be returned.  
In cases like:  
 - users does not exists  
 - requests already sent  
 - etc...
""",
        request_body=InputFriendRequestSerializer(),
        tags=["friend requests"],
        responses={
            201: 'Empty',
            400: """
One of errors:
 - Trying to be friend with self.
 - This user is already in friendship.
"""
        },
    )
    def post(self, request):
        serializer = InputFriendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']

        try:
            CreateFriendRequestService(
                from_user=request.user,
                to_username=username,
            ).create_request()
        except Account.DoesNotExist:
            # To avoid bruteforce we shouldn't tell user
            # that user with this username doesn't exist
            return Response(status=status.HTTP_201_CREATED)
        except errors.AlreadyFriendsError:
            raise ValidationError("This user is already a friend.")

        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Accept/decline friend request",
        request_body=InputFriendRequestUpdateSerializer(),
        tags=["friend requests"],
        responses={200: 'Empty'},
    )
    def patch(self, request):
        serializer = InputFriendRequestUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            UpdateFriendRequestService(
                **serializer.validated_data,
                user=request.user,
            ).update_friend_request()
        except errors.WrongUserError:
            raise ValidationError("Wrong user")

        return Response(status=status.HTTP_200_OK)
