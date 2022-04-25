import factory

from decimal import Decimal

from .models import Book

from datetime import datetime


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    name = 'Mastering Django'
    type = 'web'
    author = 'George, Nigel'
    publisher = 'Gnw Independent Publishing'
    published_at = datetime(2020, 7, 27)
    price: Decimal = 1865
    stock = 0
    is_vip_only = False
