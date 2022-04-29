from decimal import Decimal

from django.db import models
from django.utils import timezone

from django_fsm import FSMIntegerField, transition

from services.braintree_service import braintree_service


class OrderStateChoices(models.IntegerChoices):
    Init = 0
    Paid = 1
    Shipped = 2
    Finished = 3
    Canceled = 4
    Failed = 5


class PaymentTypeChoices(models.IntegerChoices):
    CreditCard = 0
    Transfer = 1


class Order(models.Model):
    user = models.ForeignKey('users.User', models.RESTRICT)
    state = FSMIntegerField(choices=OrderStateChoices.choices, default=OrderStateChoices.Init)
    payment_type = models.PositiveSmallIntegerField(
        choices=PaymentTypeChoices.choices,
        default=PaymentTypeChoices.CreditCard,
    )
    total_price = models.DecimalField(decimal_places=2, max_digits=7)
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def state_name(self):
        return OrderStateChoices(self.state).name

    @property
    def payment_type_name(self):
        return PaymentTypeChoices(self.payment_type).name

    @transition(
        field=state,
        source=[OrderStateChoices.Init, OrderStateChoices.Failed],
        target=OrderStateChoices.Paid,
        on_error=OrderStateChoices.Failed)
    def pay(self, payment_method_nonce: str = ''):
        if self.payment_type == PaymentTypeChoices.CreditCard:
            braintree_service.submit_for_settlement(Decimal(self.total_price), payment_method_nonce)

        elif self.payment_type == PaymentTypeChoices.Transfer:
            pass

    @transition(
        field=state,
        source=[OrderStateChoices.Init, OrderStateChoices.Failed],
        target=OrderStateChoices.Canceled)
    def cancel(self):
        pass


class OrderedItem(models.Model):
    order = models.ForeignKey('Order', models.CASCADE)
    book = models.ForeignKey('books.Book', models.RESTRICT)
    unit_price = models.DecimalField(decimal_places=2, max_digits=7)
    amount = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [['order', 'book']]
