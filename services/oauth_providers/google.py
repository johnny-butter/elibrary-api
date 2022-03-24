import requests

from django.conf import settings

from .base import OauthedUser, OauthProvider


class GoogleOauthProvider(OauthProvider):

    def get_access_token(self, code: str) -> str:
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

    def get_user_info(self, access_tokrn: str) -> OauthedUser:
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
