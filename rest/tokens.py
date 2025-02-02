from main.settings import SECRET_KEY, JWT_ALGORITHM
from rest.constance import CONSTANCE_CONFIG
import jwt
import uuid
import datetime

class TokensGenerator:

    @classmethod
    def gen_tokens(cls, user):
        access_token = jwt.encode({"email": user.email,
                                   "exp": datetime.datetime.utcnow() + datetime.timedelta(
                                       seconds=CONSTANCE_CONFIG['ACCESS_EXPIRE_TIME_SECONDS'][0])},
                                  SECRET_KEY,
                                  algorithm=JWT_ALGORITHM)
        refresh_token = uuid.uuid4()
        user.refresh_token = refresh_token
        user.save()
        tokens = {"access_token": access_token,
                  "refresh_token": refresh_token
                  }
        return tokens