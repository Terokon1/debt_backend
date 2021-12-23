from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import OutputAccountShortSerializer


class FriendAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List of friends",
        tags=["friends"],
        responses={200: OutputAccountShortSerializer(many=True)}
    )
    def get(self, request):
        user = request.user
        friends = user.friends.all()

        serializer = OutputAccountShortSerializer(friends, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
