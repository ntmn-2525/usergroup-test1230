from django.db import models

# Create your models here.

class LineFriend(models.Model):
    user_id = models.CharField(
        primary_key = True,
        blank = False,
        max_length = 256,
    )

    created_at = models.DateTimeField(
        auto_now_add = True,
        editable = False,
    )

    updated_at = models.DateTimeField(
        auto_now = True,
    )

    bot_name = models.CharField(
        blank = False,
        max_length = 32,
    )

class Category(models.Model):
    code = models.DecimalField(
        primary_key = True,
        blank = False,
        max_digits = 2,
        decimal_places = 2,
    )

    name = models.CharField(
        null = False,
        blank = False,
        max_length = 64,
    )
