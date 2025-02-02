from rest_framework import serializers


class UserRegisterAndLoginRequestSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=32)
    email = serializers.EmailField(max_length=32)


class UserRegisterResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()


class LoginAndRefreshResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.UUIDField()


class LogOutAndRefreshRequestSerializer(serializers.Serializer):
    refresh_token = serializers.UUIDField()


class UserMeGetRequestSerializer(serializers.Serializer):
    pass


class UserMeGetResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    username = serializers.CharField()


class UserMePutRequestSerializer(serializers.Serializer):
    password = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(max_length=32, required=False)


class UserMePutResponseSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(max_length=32)