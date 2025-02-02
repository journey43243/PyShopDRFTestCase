import datetime
import uuid

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest.tokens import TokensGenerator
from main.settings import CONSTANCE_CONFIG
from rest.serializers import *
from rest.models import CustomUser

access_expire_time = CONSTANCE_CONFIG['ACCESS_EXPIRE_TIME_SECONDS'][0]


class Register(APIView):

    @extend_schema(
        examples=[OpenApiExample('Example', description='Valid request body example',
                                 value={"email": "user@example.com", "password": "password"})],
        request=UserRegisterAndLoginRequestSerializer,
        responses={status.HTTP_201_CREATED: UserRegisterResponseSerializer})
    def post(self, request):
        serializer = UserRegisterAndLoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            new_user = CustomUser.objects.create(**request.data)
            return Response(UserRegisterResponseSerializer(new_user).data, status=status.HTTP_201_CREATED)


class User(APIView):

    @extend_schema(examples=[OpenApiExample('Example', description='You have to use header, \'cause this endpoint need it to\
                                                                   auth user in system and take user data')],
                   request=UserMeGetRequestSerializer,
                   responses={status.HTTP_200_OK: UserMeGetResponseSerializer,
                              status.HTTP_404_NOT_FOUND: {"msg": "user already exist"}})
    def get(self, request):
        serializer = UserMeGetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = request.META.get("email")
            user = get_object_or_404(CustomUser, email=email)
            return Response(UserMeGetResponseSerializer(user).data, status=status.HTTP_200_OK)

    @extend_schema(request=UserMePutRequestSerializer,
                   responses={status.HTTP_202_ACCEPTED: UserMePutResponseSerializer,
                              status.HTTP_404_NOT_FOUND: str})
    def put(self, request):
        serializer = UserMePutRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = request.META.get("email")
            CustomUser.objects.filter(email=email).update(**request.data)
            if 'email' in request.data:
                email = request.data['email']
            user = get_object_or_404(CustomUser, email=email)
            return Response(UserMePutResponseSerializer(user).data, status=status.HTTP_202_ACCEPTED)


class Login(APIView):
    # NOTICE! I know, that keeping secret key in code is dangerous, but I decided didn't replace it to more safely
    # place'cause it test case and connect .env file for one var if this case is not reasonable'

    @extend_schema(examples=[OpenApiExample('Example', description='Valid request body example',
                                 value={"email": "user@example.com", "password": "password"})],
                   request=UserRegisterAndLoginRequestSerializer,
                   responses={status.HTTP_200_OK: LoginAndRefreshResponseSerializer,
                              status.HTTP_404_NOT_FOUND: str})
    def post(self, request):
        serializer = UserRegisterAndLoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            email, password = request.data['email'], request.data['password']
            user = get_object_or_404(CustomUser, email=email)
            if user.check_password(password):
                tokens = TokensGenerator.gen_tokens(user)
                return Response(LoginAndRefreshResponseSerializer(tokens).data, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "wrong password"}, status=status.HTTP_401_UNAUTHORIZED)


class LogOut(APIView):

    @extend_schema(examples=[OpenApiExample("Example", description="Use early given refresh token",
                                            value={"refresh_token": uuid.uuid4()})],
                   responses=str,
                   request=LogOutAndRefreshRequestSerializer)
    def post(self, request):
        serializer = LogOutAndRefreshRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(CustomUser, refresh_token=request.data['refresh_token'])
            user.refresh_token = None
            user.save()
            return Response({"success": "User logged out."}, status=status.HTTP_200_OK)


class AccessTokenRefresh(APIView):

    @extend_schema(examples=[OpenApiExample("Example", description="Use already given refresh token",
                                            value={"refresh_token": uuid.uuid4()})],
                   request=LogOutAndRefreshRequestSerializer,
                   responses={status.HTTP_200_OK: LoginAndRefreshResponseSerializer,
                              status.HTTP_401_UNAUTHORIZED: None})
    def post(self, request):
        serializer = LogOutAndRefreshRequestSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = request.data['refresh_token']
            user = get_object_or_404(CustomUser, refresh_token=refresh_token)
            if user.refresh_start > timezone.now() - datetime.timedelta(
                    days=CONSTANCE_CONFIG['REFRESH_EXPIRE_TIME_DAYS'][0]):
                tokens = TokensGenerator.gen_tokens(user)
                return Response(LoginAndRefreshResponseSerializer(tokens).data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
