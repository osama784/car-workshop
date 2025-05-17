from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets

class User(AbstractUser):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    reset_code = models.CharField(max_length=6, blank=True, null=True)

    USERNAME_FIELD = 'email'       
    REQUIRED_FIELDS = ['username']

    def generate_reset_code(self):
        code = secrets.randbelow(1_000_000)  
        self.reset_code = f"{code:06d}"  # Pad with leading zeros
        self.save()
        return self.reset_code

class Customer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name="customer")
    phone_number = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} {self.user.username}: {self.user.email}"


    