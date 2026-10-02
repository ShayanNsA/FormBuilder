import random
from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework.authtoken.models import Token

from .models import OTP, User


def generate_otp(phone):

    last_otp = (
        OTP.objects
        .filter(phone=phone)
        .order_by("-created_at")
        .first()
    )

    if last_otp:
        if last_otp.created_at + timedelta(minutes=3) > timezone.now():
            return None

    code = str(random.randint(100000, 999999))

    OTP.objects.create(
        phone=phone,
        code=code,
        expiry_date=timezone.now() + timedelta(minutes=3),
    )

    return code


def verify_otp(phone, code):

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


def get_verified_otp_for_registration(phone):

    verification_limit = timezone.now() - timedelta(minutes=4)

    return (
        OTP.objects
        .filter(
            phone=phone,
            is_used=True,
            user__isnull=True,
            created_at__gte=verification_limit,
        )
        .order_by("-created_at")
        .first()
    )


def create_user_after_otp(phone, data, otp):

    user = User.objects.create_user(
        username=data["username"],
        password=data["password"],
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        email=data.get("email"),
        phone=phone,
        birth_date=data.get("birth_date"),
    )

    otp.user = user
    otp.save(update_fields=["user"])

    return user


def get_user_token(user):

    token, created = Token.objects.get_or_create(
        user=user
    )

    return token


def authenticate_user(username, password):

    return authenticate(
        username=username,
        password=password,
    )