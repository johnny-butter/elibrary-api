import requests
from typing import Optional
from django.conf import settings
from ninja import Schema


class OauthedUser(Schema):
    user_id: str
    email: Optional[str]


class OauthStrategy:

    def __init__(self, *, oauth_type: str) -> None:
        self.get_access_token = getattr(self, f'_{oauth_type}_get_access_token')
        self.get_user_info = getattr(self, f'_{oauth_type}_get_user_info')

        if not self.get_access_token or not self.get_user_info:
            raise ValueError(f'please check whether the oauth_type({oauth_type}) is supported')

    def auth(self, code: str) -> OauthedUser:
        access_token = self.get_access_token(code)
        authed_user = self.get_user_info(access_token)

        return authed_user

    def _google_get_access_token(self, code: str) -> str:
        # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        params = {
            'code': code,
            'client_id': settings.OAUTH_GOOGLE_CLIEN_ID,
            'client_secret': settings.OAUTH_GOOGLE_CLIEN_SECRET,
            'redirect_uri': settings.OAUTH_REDIRECT_URI,
            'grant_type': 'authorization_code',
        }

        resp = requests.post('https://oauth2.googleapis.com/token', headers=headers, params=params)

        data = resp.json()
        if not resp.ok:
            raise ValueError(data)
        access_token = data['access_token']

        return access_token

    def _google_get_user_info(self, access_tokrn: str) -> OauthedUser:
        # https://developers.google.com/people/api/rest/v1/people/get
        headers = {'Authorization': f'Bearer {access_tokrn}'}
        params = {'personFields': 'emailAddresses'}

        resp = requests.get('https://people.googleapis.com/v1/people/me', headers=headers, params=params)

        data = resp.json()
        if not resp.ok:
            raise ValueError(data)

        return OauthedUser(
            user_id=data['emailAddresses'][0]['metadata']['source']['id'],
            email=data['emailAddresses'][0]['value'],
        )

    def _fb_get_access_token(self, code: str) -> str:
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

    def _fb_get_user_info(self, access_tokrn: str) -> OauthedUser:
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
