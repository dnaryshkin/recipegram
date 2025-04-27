from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from backend.foodgram_backend.constants import (MAX_EMAIL_LENGTH,
                                                MAX_USERNAME_LENGTH,
                                                MAX_FIRSNAME_LENGTH,
                                                MAX_LASTNAME_LENGTH,
                                                )
from django.db import models


class User(AbstractUser):
    """Модель пользователя наследуемая от AbstractUser."""

    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name='Электронная почта',
    )
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        verbose_name='Ник пользователя',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя может содержать только буквы,'
                        'цифры и @/./+/-/_'
            )
        ]
    )
    first_name = models.CharField(
        max_length=MAX_FIRSNAME_LENGTH,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        max_length=MAX_LASTNAME_LENGTH,
        verbose_name='Фамилия пользователя',
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар пользователя',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('username',)
        verbose_name='пользователь'
        verbose_name_plural='Пользователи'

    def __str__(self):
        return f'Пользователь: {self.username}'