from typing import Optional


class APIException(Exception):
    status_code: int = 400
    message: str = 'something went wrong, please check!'

    def __init__(self, status_code: Optional[int] = None, message: Optional[str] = None):
        if status_code:
            self.status_code = status_code

        if message:
            self.message = message

    def get_message(self) -> str:
        return {'error_message': self.message}


class AuthFail(APIException):
    message = 'auth fail, please check username & password.'
