from django.core.files.base import ContentFile
from rest_framework import serializers
import base64

from backend.foodgram_backend.constants import MIN_TIME_COOKING
from backend.recipes.models import Tag, Ingredient, IngredientInRecipe, Recipe, \
    Favorite, RecipesInShoppingList
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


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с аватаром пользователей."""
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


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


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для указания ингредиента в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта (только чтение)."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredientinrecipe',
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'text',
            'cooking_time'
        )

        def get_is_favorited(self, obj):
            """Функция проверки нахождения рецепта в избранном."""
            user = self.context.get('request').user
            if not user.is_authenticated:
                return False
            return Favorite.objects.filter(
                user=user,
                recipe=obj
            ).exists()

        def get_is_in_shopping_cart(self, obj):
            """Функция проверки нахождения рецепта в списке покупок."""
            user = self.context.get('request').user
            if not user.is_authenticated:
                return False
            return RecipesInShoppingList.objects.filter(
                user=user,
                recipe=obj
            ).exists()


class MiniRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования рецепта."""
    ingredients = IngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, values):
        pass

    def validate_tags(self, values):
        pass

    def validate_image(self, values):
        pass

    def validate_cooking_time(self, values):
        pass

    def validate_name(self, values):
        pass

    def validate_text(self, values):
        pass

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )
