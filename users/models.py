from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'       
    REQUIRED_FIELDS = ['username']

class Customer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name="customer")
    phone_number = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} {self.user.username}: {self.user.email}"


    