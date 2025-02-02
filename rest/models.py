import datetime
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator



class CustomUser(AbstractUser):
    refresh_token = models.UUIDField(unique=True, default=uuid.uuid4, blank=True, null=True)
    refresh_start = models.DateTimeField(default=datetime.datetime.utcnow)
    username = models.CharField(error_messages={'unique': 'A user with that username already exists.'},
                                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                max_length=150,
                                unique=True, validators=[UnicodeUsernameValidator()], verbose_name='username',
                                blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, max_length=32)

    def save(self, *args, **kwargs):
        self.set_password(self.password)
        super().save(*args, **kwargs)
