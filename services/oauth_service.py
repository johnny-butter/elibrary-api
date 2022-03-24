from typing import Type

from . import oauth_providers
from .oauth_providers import OauthProvider, OauthedUser


class OauthStrategy:

    def __init__(self, *, oauth_type: str) -> None:
        self.oauth_provider = self._get_oauth_provider(oauth_type)()

    def auth(self, code: str) -> OauthedUser:
        access_token = self.oauth_provider.get_access_token(code)
        authed_user = self.oauth_provider.get_user_info(access_token)

        return authed_user

    def _get_oauth_provider(self, oauth_type: str) -> Type[OauthProvider]:
        oauth_provider_name = f'{oauth_type.capitalize()}OauthProvider'

        if not hasattr(oauth_providers, oauth_provider_name):
            raise ValueError(f'please check whether the oauth_type({oauth_type}) is supported')

        return getattr(oauth_providers, oauth_provider_name)
