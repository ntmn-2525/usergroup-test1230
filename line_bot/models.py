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

class Session(models.Model):
    id = models.AutoField(
        primary_key = True,
        default = 1,
    )

    user_id = models.ForeignKey(
        LineFriend,
        db_column = 'user_id',
        to_field = 'user_id',
        on_delete = models.deletion.CASCADE,
        unique = True,
    )

    data = models.BinaryField(
        default = '{}'.encode('utf-8'),
        null = False,
        blank = False,
    )

    created_at = models.DateTimeField(
        auto_now_add = True,
        editable = False,
    )

    updated_at = models.DateTimeField(
        auto_now = True,
    )

    expiration = models.DateTimeField(
        null = True,
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
