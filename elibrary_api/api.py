from ninja import NinjaAPI

from errors import APIException

from users.api import router as users_router
from books.api import router as books_router
from carts.api import router as carts_router
from orders.api import router as orders_router


api = NinjaAPI(title='eLibraryAPI', version='1')


@api.exception_handler(APIException)
def service_unavailable(request, exc):
    return api.create_response(request, exc.get_message(), status=exc.status_code)


api.add_router('/users/', users_router, tags=['users'])
api.add_router('/books/', books_router, tags=['books'])
api.add_router('/carts/', carts_router, tags=['carts'])
api.add_router('/orders/', orders_router, tags=['orders'])
