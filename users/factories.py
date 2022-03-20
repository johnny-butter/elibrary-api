import factory
from .models import User

from django.contrib.auth.hashers import make_password


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = 'test_user'
    password = factory.PostGenerationMethodCall('set_password', 'password')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
