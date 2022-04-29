from django.db import transaction
from django.db.models import F
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from ninja import Router

from .models import Cart
from books.models import Book
from orders.models import PaymentTypeChoices, Order, OrderedItem

from .schemas import CartIn, CartOut, DeleteCartIn, CheckoutCartIn, CheckoutCartOut

from errors import APIException

from services.auth_service import AuthJWT


router = Router(auth=AuthJWT())


@router.get('', response=CartOut)
def get_cart(request):
    items = Cart.objects.filter(user_id=request.auth['user_id']).select_related('book').all()

    total_price = sum([item.unit_price * item.amount for item in items])

    return {'data': list(items), 'total_price': total_price}


@router.put('', response={204: None})
def put_cart(request, payload: CartIn):
    if payload.amount <= 0:
        raise APIException(message='amount can not le 0')

    book = get_object_or_404(Book, id=payload.book_id)

    with cache.lock(f'cart_book_{book.id}'):
        book.refresh_from_db()

        if book.stock < payload.amount:
            raise APIException(message='stock not enough')

        with transaction.atomic():
            try:
                cart_item = Cart.objects.get(user_id=request.auth['user_id'], book=book)
            except Cart.DoesNotExist:
                if not payload.price:
                    raise APIException(message='missing "price" param')

                cart_item = Cart(
                    user_id=request.auth['user_id'],
                    book=book,
                    unit_price=payload.price,
                )

            Book.objects.filter(id=payload.book_id).update(stock=F('stock') + cart_item.amount - payload.amount)

            cart_item.amount = payload.amount
            cart_item.save()

    return 204, None


@router.delete('', response={204: None})
def delete_cart(request, payload: DeleteCartIn):
    cart_item = get_object_or_404(Cart, id=payload.cart_id)

    with transaction.atomic():
        cart_item.book.stock += cart_item.amount
        cart_item.book.save()

        cart_item.delete()

    return 204, None


@router.post('/checkout', response=CheckoutCartOut)
def checkout_cart(request, payload: CheckoutCartIn):
    user_id = request.auth['user_id']

    if payload.payment_type not in PaymentTypeChoices.names:
        raise APIException(message=f'unsupport payment type {payload.payment_type}')

    with transaction.atomic():
        cart_items = Cart.objects.filter(user_id=user_id).all()

        order = Order.objects.create(
            user_id=user_id,
            payment_type=PaymentTypeChoices[payload.payment_type],
            total_price=sum([cart_item.unit_price * cart_item.amount for cart_item in cart_items]),
        )

        OrderedItem.objects.bulk_create([
            OrderedItem(
                order=order,
                book=cart_item.book,
                unit_price=cart_item.unit_price,
                amount=cart_item.amount,
            ) for cart_item in cart_items
        ])

        cart_items.delete()

    return order
