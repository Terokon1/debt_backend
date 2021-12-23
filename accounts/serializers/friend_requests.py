from rest_framework import serializers

from accounts import constants
from accounts.serializers import OutputAccountShortSerializer


class InputFriendRequestSerializer(serializers.Serializer):
    username = serializers.CharField()


class OutputFriendRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    from_user = OutputAccountShortSerializer()
    to_user = OutputAccountShortSerializer()
    created_at = serializers.DateTimeField()


class InputFriendRequestUpdateSerializer(serializers.Serializer):
    friend_request_id = serializers.UUIDField()
    status = serializers.ChoiceField(constants.FRIEND_REQUEST_STATUS)
