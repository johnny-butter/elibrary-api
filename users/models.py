import random
import string

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.CharField(unique=True, null=True, max_length=254)


    @staticmethod
    def get_random_username() -> str:
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


class OauthRecord(models.Model):
    oauth_type = models.CharField(max_length=16)
    oauth_id = models.CharField(unique=True, null=True, max_length=24)
    user = models.ForeignKey('User', models.CASCADE)


    class Meta:
        unique_together = [['oauth_type', 'oauth_id']]
