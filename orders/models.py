from decimal import Decimal

from django.db import models
from django.utils import timezone

from django_fsm import FSMIntegerField, transition

from services.braintree_service import braintree_service


class OrderState:
    Init = 0
    Paid = 1
    Shipped = 2
    Finished = 3
    Canceled = 4
    Failed = 5


class PaymentType:
    CreditCard = 0
    Transfer = 1


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
