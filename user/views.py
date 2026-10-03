from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import User

from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
    UpdateProfileSerializer,
)

from .services import (
    generate_otp,
    verify_otp,
    get_verified_otp_for_registration,
    create_user_after_otp,
    get_user_token,
    authenticate_user,
)

from drf_spectacular.utils import extend_schema


@extend_schema(
    request=SendOTPSerializer,
)
@api_view(["POST"])
def send_otp(request):

    serializer = SendOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    phone = serializer.validated_data["phone"]

    code = generate_otp(phone)

    if code is None:
        return Response(
            {
                "error": "لطفاً قبل از درخواست OTP جدید کمی صبر کنید."
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    return Response(
        {
            "message": "OTP sent successfully.",
            "code": code,  # فقط برای تست
        },
        status=status.HTTP_200_OK
    )


@extend_schema(
    request=VerifyOTPSerializer,
)
@api_view(["POST"])
def verify_otp_view(request):

    serializer = VerifyOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    phone = serializer.validated_data["phone"]
    code = serializer.validated_data["code"]

    otp = verify_otp(phone, code)

    if otp is None:
        return Response(
            {
                "error": "Invalid or expired OTP."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {
            "message": "Phone number verified successfully.",
            "phone": phone,
        },
        status=status.HTTP_200_OK
    )


@extend_schema(
    request=RegisterSerializer,
)
@api_view(["POST"])
def register(request):

    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    phone = serializer.validated_data["phone"]

    if User.objects.filter(phone=phone).exists():
        return Response(
            {
                "error": "User with this phone already exists."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    otp = get_verified_otp_for_registration(phone)

    if otp is None:
        return Response(
            {
                "error": "شماره موبایل تأیید نشده یا زمان تأیید آن منقضی شده است."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = create_user_after_otp(
        phone=phone,
        data=serializer.validated_data,
        otp=otp,
    )

    token = get_user_token(user)

    return Response(
        {
            "message": "User registered successfully.",
            "token": token.key,
            "user": ProfileSerializer(user).data,
        },
        status=status.HTTP_201_CREATED
    )


@extend_schema(
    request=LoginSerializer,
)
@api_view(["POST"])
def login_user(request):

    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]

    user = authenticate_user(
        username=username,
        password=password,
    )

    if user is None:
        return Response(
            {
                "error": "Username or password is incorrect."
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    token = get_user_token(user)

    return Response(
        {
            "message": "Login successful.",
            "token": token.key,
        },
        status=status.HTTP_200_OK
    )


@extend_schema(
    request=ProfileSerializer,
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):

    serializer = ProfileSerializer(request.user)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )



@extend_schema(
    request=UpdateProfileSerializer,
)
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):

    serializer = UpdateProfileSerializer(
        request.user,
        data=request.data,
        partial=True
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save()

    return Response(
        ProfileSerializer(request.user).data,
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):

    Token.objects.filter(
        user=request.user
    ).delete()

    return Response(
        {
            "message": "Logout successful."
        },
        status=status.HTTP_200_OK
    )