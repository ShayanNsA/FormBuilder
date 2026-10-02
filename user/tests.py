from datetime import timedelta

from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import User, OTP


class UserAPITest(APITestCase):

    def test_send_otp(self):
        response = self.client.post(
            "/api/accounts/send-otp/",
            {"phone": "09123456789"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("code", response.data)

        self.assertTrue(
            OTP.objects.filter(phone="09123456789").exists()
        )

    def test_send_otp_invalid_phone(self):
        response = self.client.post(
            "/api/accounts/send-otp/",
            {"phone": "123456789"}
        )

        self.assertEqual(response.status_code, 400)

    def test_send_otp_rate_limit(self):
        OTP.objects.create(
            phone="09123456789",
            code="123456",
            expiry_date=timezone.now() + timedelta(minutes=3),
        )

        response = self.client.post(
            "/api/accounts/send-otp/",
            {"phone": "09123456789"}
        )

        self.assertEqual(response.status_code, 429)

    def test_verify_otp(self):
        OTP.objects.create(
            phone="09123456789",
            code="123456",
            expiry_date=timezone.now() + timedelta(minutes=3),
        )

        response = self.client.post(
            "/api/accounts/verify-otp/",
            {"phone": "09123456789", "code": "123456"}
        )

        self.assertEqual(response.status_code, 200)

        otp = OTP.objects.get(phone="09123456789")

        self.assertTrue(otp.is_used)

    def test_verify_otp_wrong_code(self):
        OTP.objects.create(
            phone="09123456789",
            code="123456",
            expiry_date=timezone.now() + timedelta(minutes=3),
        )

        response = self.client.post(
            "/api/accounts/verify-otp/",
            {"phone": "09123456789", "code": "999999"}
        )

        self.assertEqual(response.status_code, 400)

    def test_register_success(self):
        otp = OTP.objects.create(
            phone="09123456789",
            code="123456",
            expiry_date=timezone.now() + timedelta(minutes=3),
            is_used=True,
        )

        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "shayan",
                "password": "12345678",
                "first_name": "Shayan",
                "last_name": "Test",
                "email": "shayan@test.com",
                "birth_date": "2005-01-01",
                "phone": "09123456789",
            }
        )

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username="shayan")

        self.assertEqual(user.phone, "09123456789")
        self.assertEqual(user.first_name, "Shayan")
        self.assertEqual(user.email, "shayan@test.com")

        otp.refresh_from_db()

        self.assertEqual(otp.user, user)
        self.assertIn("token", response.data)

    def test_register_without_verified_otp(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "shayan",
                "password": "12345678",
                "first_name": "Shayan",
                "last_name": "Test",
                "email": "shayan@test.com",
                "birth_date": "2005-01-01",
                "phone": "09123456789",
            }
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(
            User.objects.filter(username="shayan").exists()
        )

    def test_register_invalid_data(self):
        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "",
                "password": "",
                "phone": "123456789"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_phone(self):
        User.objects.create_user(
            username="old_user",
            password="12345678",
            phone="09123456789",
        )

        response = self.client.post(
            "/api/accounts/register/",
            {
                "username": "new_user",
                "password": "12345678",
                "first_name": "New",
                "last_name": "User",
                "email": "new@test.com",
                "birth_date": "2005-01-01",
                "phone": "09123456789",
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        user = User.objects.create_user(
            username="shayan",
            password="12345678",
        )

        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": "shayan",
                "password": "12345678",
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

        self.assertTrue(
            Token.objects.filter(user=user).exists()
        )

    def test_login_wrong_password(self):
        User.objects.create_user(
            username="shayan",
            password="12345678",
        )

        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": "shayan",
                "password": "wrong-password",
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_profile(self):
        user = User.objects.create_user(
            username="shayan",
            password="12345678",
            first_name="Shayan",
            last_name="Test",
        )

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.get("/api/accounts/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "shayan")
        self.assertEqual(response.data["first_name"], "Shayan")

    def test_profile_without_authentication(self):
        response = self.client.get("/api/accounts/profile/")

        self.assertEqual(response.status_code, 401)

    def test_update_profile(self):
        user = User.objects.create_user(
            username="shayan",
            password="12345678",
            first_name="Old",
        )

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.patch(
            "/api/accounts/profile/update/",
            {
                "first_name": "New",
                "last_name": "Test",
            }
        )

        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()

        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "Test")

    def test_logout(self):
        user = User.objects.create_user(
            username="shayan",
            password="12345678",
        )

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        response = self.client.post("/api/accounts/logout/")

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Token.objects.filter(user=user).exists()
        )