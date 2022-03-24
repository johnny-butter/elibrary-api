import abc

from typing import Optional, Type

from ninja import Schema


class OauthedUser(Schema):
    user_id: str
    email: Optional[str]


class OauthProvider(abc.ABC):

    @abc.abstractmethod
    def get_access_token(self, code: str) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_user_info(self, access_tokrn: str) -> Type[OauthedUser]:
        raise NotImplementedError()
