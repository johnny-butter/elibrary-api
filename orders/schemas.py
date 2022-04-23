from ninja import Schema, ModelSchema

from .models import Order


class OrderIn(Schema):
    order_id: int


class OrderOut(ModelSchema):
    class Config:
        model = Order
        model_exclude = ['user']


class OrderPayIn(Schema):
    order_id: int
    payment_method_nonce: str
