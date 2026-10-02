import random
from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework.authtoken.models import Token

from .models import OTP, User


def generate_otp(phone):
    """
    Create a new OTP for a phone number.
    """

    code = str(random.randint(100000, 999999))

    OTP.objects.create(
        phone=phone,
        code=code,
        expiry_date=timezone.now() + timedelta(minutes=3),
    )

    return code


def verify_otp(phone, code):
    """
    Check whether the OTP is valid.
    """

    try:
        otp = OTP.objects.get(
            phone=phone,
            code=code,
            is_used=False,
        )
    except OTP.DoesNotExist:
        return None

    if otp.expiry_date < timezone.now():
        return None

    otp.is_used = True
    otp.save(update_fields=["is_used"])

    return otp


def create_user_after_otp(phone, data):
    """
    Create a user after successful OTP verification.
    """

    user = User.objects.create_user(
        username=data["username"],
        password=data["password"],
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        email=data.get("email"),
        phone=phone,
        birth_date=data.get("birth_date"),
    )

    return user


def get_user_token(user):
    """
    Get or create authentication token for user.
    """

    token, created = Token.objects.get_or_create(
        user=user
    )

    return token


def authenticate_user(username, password):
    """
    Authenticate user with username and password.
    """

    return authenticate(
        username=username,
        password=password,
    )