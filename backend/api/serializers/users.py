from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from backend.api.serializers.base64 import Base64ImageField
from backend.foodgram_backend.constants import MAX_EMAIL_LENGTH, \
    MAX_USERNAME_LENGTH, MAX_LASTNAME_LENGTH
from backend.users.models import User, Subscription


class ReadUserSerializer(serializers.ModelSerializer):
    """Сериализатор для получения профиля Пользователя (только чтение)."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = '__all__'

    def get_is_subscribed(self, obj):
        """Функция проверки подписки пользователя на автора."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(
                user=user,
                following=obj
            ).exists()
        return False


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания профиля пользователя."""
    email = serializers.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже зарегистрирован!'
            )
        ],
    )
    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя может содержать только буквы, '
                        'цифры и "@.+-_"'
            ),
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким ником уже зарегистрирован!'
            )
        ],
    )
    first_name = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=MAX_LASTNAME_LENGTH,
        required=True,
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )

    def create(self, validated_data):
        """Функция создания пользователя."""
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с аватаром пользователей."""
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
