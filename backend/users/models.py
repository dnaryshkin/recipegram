from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from foodgram_backend.constants import (
    MAX_EMAIL_LENGTH,
    MAX_FIRSNAME_LENGTH,
    MAX_LASTNAME_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
)


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
                message='Имя пользователя может содержать только буквы, '
                        'цифры и "@.+-_"'
            )
        ],
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
    password = models.CharField(
        max_length=MAX_PASSWORD_LENGTH,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'Пользователь: {self.username}'


class Subscription(models.Model):
    """Модель подписок между пользователями."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followings',
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'подписка пользователя'
        verbose_name_plural = 'Подписки пользователя'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return (f'Пользователь: {self.user.username} '
                f'подписан на {self.following.username}')
