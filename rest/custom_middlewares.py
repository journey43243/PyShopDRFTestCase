import jwt
from rest_framework.response import Response
from rest_framework import status
from main.settings import SECRET_KEY, JWT_ALGORITHM
from rest_framework.renderers import JSONRenderer


class CheckTokenMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.headers.get('Authorization', False)
        try:
            if auth:
                access_token = auth.split()[1]
                email = jwt.decode(access_token, SECRET_KEY, algorithms=JWT_ALGORITHM)['email']

                request.META["email"] = email
                response = self.get_response(request)
                return response
            else:
                response = self.get_response(request)
                return response

        except jwt.exceptions.PyJWTError:
            response = Response({"msg": "invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}
            response.render()
            return response
