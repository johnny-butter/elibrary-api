from errors import APIException
from ninja import NinjaAPI

from errors import APIException

from users.api import router as users_router


api = NinjaAPI(title= 'eLibraryAPI', version='1')

@api.exception_handler(APIException)
def service_unavailable(request, exc):
    return api.create_response(request, exc.get_message(), status=exc.status_code)

api.add_router('/users/', users_router, tags=['users'])
