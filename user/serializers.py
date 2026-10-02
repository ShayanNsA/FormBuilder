from django.core.validators import RegexValidator
from rest_framework import serializers

from .models import User


phone_validator = RegexValidator(
    regex=r"09\d{9}",
    message="یک شماره معتبر وارد کنید! برای مثال 09123456789"
)


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=11,
        validators=[phone_validator]
    )


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=11,
        validators=[phone_validator]
    )
    code = serializers.CharField(
        max_length=6,
        min_length=6
    )


class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=11,
        validators=[phone_validator]
    )

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "phone",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True
    )


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "birth_date",
        ]


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "birth_date",
        ]

        extra_kwargs = {
            "first_name": {
                "required": False
            },
            "last_name": {
                "required": False
            },
            "email": {
                "required": False
            },
            "birth_date": {
                "required": False
            },
        }