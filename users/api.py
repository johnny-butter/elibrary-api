import jwt

from ninja import Router

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db import transaction

from services.auth_service import AuthJWT
from services.oauth_service import OauthStrategy

from errors import AuthFail, APIException

from .models import User, OauthRecord
from .schemas import AuthIn, AuthOut, UserIn, UserOut, RegisterUserIn


router = Router()

@router.post("/auth", response=AuthOut)
def auth(request, payload: AuthIn):
    user = None

    if payload.oauth_type:
        try:
            oauthed_user = OauthStrategy(oauth_type=payload.oauth_type).auth(payload.oauth_code)
        except ValueError as e:
            raise APIException(message=str(e))

        oauth_record = get_object_or_404(OauthRecord, oauth_type=payload.oauth_type, oauth_id=oauthed_user.user_id)
        user = oauth_record.user
    else:
        user = authenticate(request, username=payload.username, password=payload.password)

    if user is None:
        raise AuthFail()

    jwt_token = _get_jwt_token(user)

    return {'token': jwt_token}


@router.post('', response=AuthOut)
def create_user(request, payload: RegisterUserIn):
    user = None

    if (payload.oauth_code):
        try:
            oauthed_user = OauthStrategy(oauth_type=payload.oauth_type).auth(payload.oauth_code)
        except ValueError as e:
            raise APIException(message=str(e))

        with transaction.atomic():
            oauth_record = OauthRecord.objects.create(
                oauth_type = payload.oauth_type,
                oauth_id = oauthed_user.user_id,
                user = User.objects.create(
                    username = User.get_random_username(),
                    password = '',
                    email = oauthed_user.email,
                ),
            )

            user = oauth_record.user
    else:
        password = payload.dict().pop('password')

        user = User.objects.create(**payload.dict(exclude={'oauth_type', 'oauth_code'}))
        user.set_password(password)
        user.save()

    if user is None:
        raise APIException(message='register fail, please check!')

    jwt_token = _get_jwt_token(user)

    return {'token': jwt_token}


@router.get('', response=UserOut, auth=AuthJWT())
def get_user(request):
    user = get_object_or_404(User, id=request.auth['user_id'])

    return user


@router.put('', response=UserOut, auth=AuthJWT())
def update_user(request, payload: UserIn):
    user = get_object_or_404(User, id=request.auth['user_id'])

    for attr, value in payload.dict().items():
        if attr == 'password':
            if len(value) > 0:
                user.set_password(value)

            continue

        setattr(user, attr, value)

    user.save()

    return user


def _get_jwt_token(user: User):
    payload = {'user_id': user.id}

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token
