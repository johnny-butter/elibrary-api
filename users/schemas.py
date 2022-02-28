from typing import Optional
from ninja import Schema


class AuthIn(Schema):
    username: Optional[str]
    password: Optional[str]
    oauth_type: Optional[str]
    oauth_code: Optional[str]


class AuthOut(Schema):
    token: str


class UserIn(Schema):
    username: str
    password: str
    first_name: str = ''
    last_name: str = ''
    email: str
    is_staff: bool = False


class RegisterUserIn(UserIn):
    username: Optional[str]
    password: Optional[str]
    email: Optional[str]
    oauth_type: Optional[str]
    oauth_code: Optional[str]


class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: Optional[str]
    is_staff: bool
