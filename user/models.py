from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    phone = models.CharField(max_length=11, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.username


class OTP(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='otps')

    code = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    expiry_date = models.DateTimeField()

    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.phone} - {self.code}"