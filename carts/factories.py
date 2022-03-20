import factory
from .models import Cart

from users.factories import UserFactory
from books.factories import BookFactory


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)
    book = factory.SubFactory(BookFactory)
    unit_price = 100
    amount = 1
