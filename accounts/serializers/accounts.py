from rest_framework import serializers


class InputAccountRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class OutputAccountShortSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField()


OutputAccountSerializer = OutputAccountShortSerializer
