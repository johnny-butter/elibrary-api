from django.db import models
from django.utils import timezone

from django_fsm import FSMIntegerField


class OrderState:
    Init = 0
    Paid = 1
    Shipped = 2
    Finished = 3
    Canceled = 4


class PaymentType:
    CreditCard = 0
    Cash = 1


class Cart(models.Model):
    user = models.ForeignKey('users.User', models.CASCADE)
    book = models.ForeignKey('books.Book', models.RESTRICT)
    unit_price = models.PositiveIntegerField(default=0)
    amount = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [['user', 'book']]


class Order(models.Model):
    user = models.ForeignKey('users.User', models.RESTRICT)
    state = FSMIntegerField(default=OrderState.Init)
    payment_type = models.PositiveSmallIntegerField(default=PaymentType.CreditCard)
    total_price = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)


class OrderedItem(models.Model):
    order = models.ForeignKey('Order', models.CASCADE)
    book = models.ForeignKey('books.Book', models.RESTRICT)
    unit_price = models.PositiveIntegerField(default=0)
    amount = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [['order', 'book']]
