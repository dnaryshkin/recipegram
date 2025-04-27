from django.core.files.base import ContentFile
from rest_framework import serializers
import base64

from backend.recipes.models import Tag, Ingredient
from backend.users.models import User, Subscription


class Base64ImageField(serializers.ImageField):
    """Сериализатор для изображений в формате base64."""
    def to_internal_value(self, data):
        """Функция декодирования данных base64."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Пользователя."""
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

    def get_is_subscribed(self, obj):
        """Функция проверки подписки пользователя на автора."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(
                user=user,
                following=obj
            ).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Сериадизатор для модели Тега (только чтение)."""

    class Meta:
        model = Tag
        fields = ('id','name', 'slug')
        read_only_fields = ('id','name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ингредиент (только чтение)."""

    class Meta:
        model = Ingredient
        fields = ('id','name','measurement_unit')
        read_only_fields = ('id','name','measurement_unit')



