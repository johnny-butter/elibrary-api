import requests

from django.conf import settings

from .base import OauthedUser, OauthProvider


class FbOauthProvider(OauthProvider):

    def get_access_token(self, code: str) -> str:
        # https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
        params = {
            'code': code,
            'client_id': settings.OAUTH_FB_CLIEN_ID,
            'client_secret': settings.OAUTH_FB_CLIEN_SECRET,
            'redirect_uri': settings.OAUTH_REDIRECT_URI,
        }

        resp = requests.get('https://graph.facebook.com/v13.0/oauth/access_token', params=params)

        data = resp.json()
        if not resp.ok:
            raise ValueError(data)
        access_token = data['access_token']

        return access_token

    def get_user_info(self, access_tokrn: str) -> OauthedUser:
        # https://developers.facebook.com/docs/graph-api/overview/
        # https://developers.facebook.com/docs/graph-api/reference/user/
        resp = requests.get(f'https://graph.facebook.com/me?access_token={access_tokrn}')

        data = resp.json()
        if not resp.ok:
            raise ValueError(data)
        user_id = data['id']

        user_resp = requests.get(f'https://graph.facebook.com/v13.0/{user_id}/?access_token={access_tokrn}')

        user_data = resp.json()
        if not resp.ok:
            raise ValueError(user_data)

        return OauthedUser(
            user_id=user_id,
            email=user_data.get('email', None),
        )
