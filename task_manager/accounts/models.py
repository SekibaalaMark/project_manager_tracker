from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ("OWNER", "Owner"),
        ("MANAGER", "Manager"),
        ("MEMBER", "Member"),
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        null=True,
        blank=True
    )

    username = models.CharField(max_length=40,unique=True)

    def __str__(self):
        return self.username
