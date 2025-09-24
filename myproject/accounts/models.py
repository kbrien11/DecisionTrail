from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True)
    company = models.CharField(max_length=50, blank=True, unique=True)

    def __str__(self):
        return self.username
