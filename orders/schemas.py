from decimal import Decimal
from typing import List
from ninja import Field, Schema, ModelSchema

from .models import Order


class OrderIn(Schema):
    order_id: int


class OrderBook(Schema):
    name: str
    type: str


class OrderedItem(Schema):
    book: OrderBook
    price: Decimal = Field(..., alias='unit_price')
    amount: int


class OrderOut(ModelSchema):
    id: int
    state: str = Field(..., alias='state_name')
    payment_type: str = Field(..., alias='payment_type_name')
    ordered_items: List[OrderedItem] = Field(..., alias='ordereditem_set')

    class Config:
        model = Order
        model_exclude = ['user']


class OrderPayIn(Schema):
    order_id: int
    payment_method_nonce: str
