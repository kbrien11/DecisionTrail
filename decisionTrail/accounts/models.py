from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=20)
    username = models.CharField(unique=True, max_length=20)
    company = models.CharField(max_length=50, blank=True, unique=True)
    projects = ArrayField(
        base_field=models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text="List of projects the user has access to",
    )

    def __str__(self):
        return self.username
