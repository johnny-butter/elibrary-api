from decimal import Decimal
from typing import List, Optional
from ninja import Schema, Field


class CartIn(Schema):
    book_id: int
    price: Optional[Decimal]
    amount: int


class CartBook(Schema):
    id: int
    name: str


class CartItem(Schema):
    id: int
    book: CartBook
    price: Decimal = Field(..., alias='unit_price')
    amount: int


class CartOut(Schema):
    data: List[CartItem]
    total_price: Decimal


class DeleteCartIn(Schema):
    cart_id: int


class CheckoutCartIn(Schema):
    payment_type: str


class CartOrderedItem(Schema):
    book: CartBook
    price: Decimal = Field(..., alias='unit_price')
    amount: int


class CheckoutCartOut(Schema):
    order_id: int = Field(..., alias='id')
    total_price: Decimal
    items: List[CartOrderedItem] = Field(..., alias='ordereditem_set')
