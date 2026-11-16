
from django.db import models


class MealMateUser(models.Model):
    id = models.AutoField(
        primary_key=True
    )

    full_name = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        max_length=255,
        unique=True
    )

    password_hash = models.CharField(
        max_length=255
    )

    role = models.CharField(
        max_length=30,
        default="user"
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "users"
