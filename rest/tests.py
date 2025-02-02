import random
import uuid

from django.template.context_processors import request
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
import jwt
from main.settings import SECRET_KEY, JWT_ALGORITHM
from rest.models import CustomUser
from rest.tokens import TokensGenerator
from rest.serializers import UserMePutRequestSerializer


class TestEndpointsPositives(TestCase):
    register_and_login_params = [("password", "user1@example.com"),
                                 ("password", "user2@example.com"),
                                 ("password", "user3@example.com"),
                                 ("password", "user4@example.com"),
                                 ("password", "user5@example.com")]

    put_fields = [field for field in UserMePutRequestSerializer().get_fields()]

    def create_user_fixture(self, password, email):
        data = {"password": password,
                "email": email}
        user = CustomUser.objects.create(**data)  # This is positive test and I have to create user, before run test
        return user

    def set_user_refresh_token_fixture(self, user):
        refresh_token = uuid.uuid4()
        user.refresh_token = refresh_token
        user.save()
        return user

    def test_register_endpoint(self):
        url = reverse('register')
        increm = 1
        for passw, email in self.register_and_login_params:
            response = self.client.post(url,
                                        data={"password": passw,
                                              "email": email},
                                        content_type="application/json",
                                        format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data, {"id": increm, "email": email})
            increm += 1

    def test_login_endpoint(self):
        url = reverse('login')
        for passw, email in self.register_and_login_params:
            user = self.create_user_fixture(passw, email)
            data = {"password": passw,
                    "email": user.email}
            response = self.client.post(url,
                                        data=data,
                                        content_type="application/json",
                                        format="json")
            token = jwt.decode(response.data["access_token"],
                               SECRET_KEY,
                               JWT_ALGORITHM)  # Let me explain: method decode have to throw exception if token is unvalid
            user = CustomUser.objects.get(email=token["email"])
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(email, token["email"])
            self.assertEqual(str(user.refresh_token), response.data["refresh_token"])

    def test_access_refresh_endpoint(self):
        url = reverse('refresh-access')
        for passw, email in self.register_and_login_params:
            user = self.create_user_fixture(passw, email)
            data = {"refresh_token": user.refresh_token}
            response = self.client.post(url,
                                        data=data,
                                        content_type="application/json",
                                        format="json")
            jwt.decode(response.data["access_token"], SECRET_KEY, JWT_ALGORITHM)
            user_with_new_token = CustomUser.objects.get(refresh_token=response.data["refresh_token"])
            self.assertEqual(user.email, user_with_new_token.email)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_endpoint(self):
        url = reverse('logout')
        for passw, email in self.register_and_login_params:
            user_without_refresh_token = self.create_user_fixture(passw, email)
            user = self.set_user_refresh_token_fixture(user_without_refresh_token)
            data = {"refresh_token": user.refresh_token}
            response = self.client.post(url,
                                        data=data,
                                        content_type="application/json",
                                        format="json")
            user = CustomUser.objects.get(email=email)
            self.assertIsNone(user.refresh_token)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_me_get_endpoint(self):
        url = reverse('me')
        for passw, email in self.register_and_login_params:
            user = self.create_user_fixture(passw, email)
            tokens = TokensGenerator.gen_tokens(user)
            response = self.client.get(url, HTTP_Authorization=f"Bearer {tokens.get('access_token')}",
                                       content_type="application/json",
                                       format="json"
                                       )
            self.assertEqual(user.id, response.data['id'])
            self.assertEqual(user.username, response.data['username'])
            self.assertEqual(user.email, response.data['email'])

    def test_me_put_endpoint(self):
        url = reverse('me')
        for passw, email in self.register_and_login_params:
            user = self.create_user_fixture(passw, email)
            index = random.randint(0, len(self.put_fields) - 1)
            field = self.put_fields[index]
            self.put_fields.pop(index)
            if field != 'email':
                new_val = 'test' + str(random.random())
            else:
                new_val = f'test{random.randint(0, 10)}@mail.ru'

            data = {field: new_val}
            tokens = TokensGenerator.gen_tokens(user)
            response = self.client.put(url, data=data, HTTP_Authorization=f"Bearer {tokens.get('access_token')}",
                                       content_type="application/json",
                                       format="json")
            user = CustomUser.objects.get(refresh_token=tokens['refresh_token'])
            self.assertEqual(user.id, response.data['id'])
            self.assertEqual(user.email, response.data['email'])
            if field != 'password':
                self.assertEqual(new_val, response.data[field])
            else:
                self.assertEqual(user.password, new_val)

