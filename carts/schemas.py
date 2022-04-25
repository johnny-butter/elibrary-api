from decimal import Decimal
from typing import List, Optional
from ninja import Schema, Field


class CartIn(Schema):
    book_id: int
    price: Optional[Decimal]
    amount: int


class Book(Schema):
    id: int
    name: str


class CartItem(Schema):
    id: int
    book: Book
    price: Decimal = Field(..., alias='unit_price')
    amount: int


class CartOut(Schema):
    data: List[CartItem]
    total_price: Decimal


class DeleteCartIn(Schema):
    cart_id: int


class CheckoutCartIn(Schema):
    payment_type: str


class OrderedItem(Schema):
    book: Book
    price: Decimal = Field(..., alias='unit_price')
    amount: int


class CheckoutCartOut(Schema):
    order_id: int = Field(..., alias='id')
    total_price: Decimal
    items: List[OrderedItem] = Field(..., alias='ordereditem_set')
