from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=20)
    username = models.CharField(unique=True, max_length=20)
    company = models.CharField(max_length=50, blank=True, unique=True)

    def __str__(self):
        return self.username
