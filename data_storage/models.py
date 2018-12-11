from django.db import models
from django.core import validators
from django.utils import timezone

class Category(models.Model):
    id = models.AutoField(
        primary_key = True,
        default = 1,
    )

    code = models.IntegerField(
        unique = True,
        null = False,
        validators = [
            validators.MinValueValidator(1),
            validators.MaxValueValidator(5),
        ],
    )

    name = models.CharField(
        null = False,
        blank = False,
        max_length = 64,
    )

class Advice(models.Model):
    id = models.AutoField(
        primary_key = True,
        default = 1,
    )

    category_code = models.ForeignKey(
        Category,
        db_column='category_code',
        to_field='code',
        on_delete = models.deletion.CASCADE,
    )

    code = models.IntegerField(
        null = False,
        validators = [
            validators.MinValueValidator(1),
            validators.MaxValueValidator(30),
        ],
    )

    content = models.CharField(
        null = False,
        blank = False,
        max_length = 64,
    )

    sentence = models.CharField(
        null = False,
        blank = False,
        max_length = 256,
    )

    class Meta:
        unique_together = (('category_code', 'code'))

class LineFriend(models.Model):
    id = models.AutoField(
        primary_key = True,
        default = 1,
    )

    user_id = models.CharField(
        unique = True,
        null = False,
        blank = False,
        max_length = 256,
    )

    created_at = models.DateTimeField(
        default = timezone.now,
    )

    updated_at = models.DateTimeField(
        null = True,
    )

    favorite_category_code = models.ForeignKey(
        Category,
        db_column='favorite_category_code',
        to_field='code',
        on_delete = models.deletion.CASCADE,
        null = True,
    )

    asking = models.BooleanField(
        default = False,
    )
