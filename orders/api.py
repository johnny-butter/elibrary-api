from typing import List

from ninja import Router

from django.shortcuts import get_object_or_404

from .schemas import OrderIn, OrderOut, OrderPayIn

from .models import Order

from services.auth_service import AuthJWT

from errors import APIException


router = Router(auth=AuthJWT())


@router.get('', response=List[OrderOut])
def orders(request):
    orders = Order.objects \
        .prefetch_related('ordereditem_set', 'ordereditem_set__book') \
        .filter(user_id=request.auth['user_id'])

    return orders


@router.post('/pay', response={204: None})
def pay(request, payload: OrderPayIn):
    order = get_object_or_404(Order, id=payload.order_id, user_id=request.auth['user_id'])

    try:
        order.pay(payload.payment_method_nonce)
    except Exception as e:
        raise APIException(message=str(e))
    finally:
        order.save()

    return 204, None


@router.post('/cancel', response={204: None})
def cancel(request, payload: OrderIn):
    order = get_object_or_404(Order, id=payload.order_id, user_id=request.auth['user_id'])

    try:
        order.cancel()
    except Exception as e:
        raise APIException(message=str(e))

    order.save()

    return 204, None
