import jwt

from ninja import Router

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from services.auth_service import AuthJWT
from errors import AuthFail

from .models import User
from .schemas import AuthIn, AuthOut, UserIn, UserOut


router = Router()

@router.post("/auth", response=AuthOut)
def auth(request, payload: AuthIn):
    user = authenticate(request, username=payload.username, password=payload.password)

    if user is None:
        raise AuthFail

    payload = {'user_id': user.id}

    jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return {'token': jwt_token}


@router.post('', response=UserOut)
def create_user(request, payload: UserIn):
    password = payload.dict().pop('password')

    user = User.objects.create(**payload.dict())
    user.set_password(password)
    user.save()

    return user


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
