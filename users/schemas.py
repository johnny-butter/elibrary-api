from ninja import Schema


class AuthIn(Schema):
    username: str
    password: str


class AuthOut(Schema):
    token: str


class UserIn(Schema):
    username: str
    password: str
    first_name: str
    last_name: str
    email: str
    is_staff: bool = False


class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    is_staff: bool
