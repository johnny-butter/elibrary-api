from django.db import transaction
from django.db.models import F
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from ninja import Router

from .models import Cart, Order
from books.models import Book

from .schemas import CartIn, CartOut, DeleteCartIn, CheckoutCartOut

from errors import APIException

from services.auth_service import AuthJWT


router = Router()


@router.get('', response=CartOut, auth=AuthJWT())
def get_cart(request):
    query = Cart.objects.filter(user_id=request.auth['user_id']).select_related('book').all()

    return {'data': list(query)}


@router.put('', response={204: None}, auth=AuthJWT())
def put_cart(request, payload: CartIn):
    if payload.amount <= 0:
        raise APIException(message='amount can not le 0')

    book = get_object_or_404(Book, id=payload.book_id)

    with cache.lock(f'cart_book_{book.id}'):
        book.refresh_from_db()

        if book.stock < payload.amount:
            raise APIException(message='stock not enough')

        with transaction.atomic():
            cart_item, is_created = Cart.objects.get_or_create(
                user_id=request.auth['user_id'],
                book=book,
            )

            if is_created and not payload.price:
                raise APIException(message='missing "price" param')

            Book.objects.filter(id=payload.book_id).update(stock=F('stock') + cart_item.amount - payload.amount)

            if is_created:
                cart_item.unit_price = payload.price

            cart_item.amount = payload.amount
            cart_item.save()

    return 204, None


@router.delete('', response={204: None}, auth=AuthJWT())
def delete_cart(request, payload: DeleteCartIn):
    cart_item = get_object_or_404(Cart, id=payload.cart_id)

    with transaction.atomic():
        cart_item.book.stock += cart_item.amount
        cart_item.book.save()

        cart_item.delete()

    return 204, None


@router.post('/checkout', response=CheckoutCartOut, auth=AuthJWT())
def checkout_cart(request):
    user_id = request.auth['user_id']

    with transaction.atomic():
        order = Order.objects.create(user_id=user_id)

        cart_items = Cart.objects.filter(user_id=user_id).all()

        for cart_item in cart_items:
            order.ordereditem_set.create(
                book=cart_item.book,
                unit_price=cart_item.unit_price,
                amount=cart_item.amount,
            )

            order.total_price += cart_item.unit_price * cart_item.amount

        order.save()
        cart_items.delete()

    return order
