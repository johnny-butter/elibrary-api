class APIException(Exception):
    status_code: int = 400
    message: str = 'something went wrong, please check!'

    def get_message(self) -> str:
        return {'error_message': self.message}


class AuthFail(APIException):
    message = 'auth fail, please check username & password.'
