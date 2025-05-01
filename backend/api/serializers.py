from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from rest_framework import serializers
import base64

from rest_framework.validators import UniqueValidator

from backend.foodgram_backend.constants import MIN_TIME_COOKING, \
    MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH, MAX_LASTNAME_LENGTH, MIN_AMOUNT_INGREDIENTS
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


class TagSerializer(serializers.ModelSerializer):
    """Сериадизатор для модели Тега (только чтение)."""

    class Meta:
        model = Tag
        fields = ('id','name', 'slug')
        read_only_fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ингредиент (только чтение)."""

    class Meta:
        model = Ingredient
        fields = ('id','name','measurement_unit')
        read_only_fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для указания ингредиента в рецепте."""
    id = serializers.ReadOnlyField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта (только чтение)."""
    tags = TagSerializer(many=True, read_only=True)
    author = ReadUserSerializer(read_only=True)
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
    ingredients = IngredientRecipeSerializer(
        many=True,
    )
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
        """Функция проверки поля ингредиентов."""
        if not values:
            raise serializers.ValidationError(
                'Необходимо указать ингредиенты!'
            )
        ingredients = [item['ingredient'] for item in values]
        if len(ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!'
            )
        if len(ingredients) < MIN_AMOUNT_INGREDIENTS:
            raise serializers.ValidationError(
                f'Ингредиентов должно быть не меньше {MIN_AMOUNT_INGREDIENTS}'
            )
        return values

    def validate_tags(self, values):
        """Функция проверки поля тегов."""
        if not values:
            raise serializers.ValidationError(
                'Необходимо указать тег!'
            )
        if len(values) != len(set(values)):
            raise serializers.ValidationError(
                'Теги не должны повторяться'
            )
        return values

    def validate_image(self, values):
        """Функция проверки изображений рецепта."""
        if not values:
            raise serializers.ValidationError(
                'Необходимо добавить изображение рецепта!'
            )
        return values

    def validate_cooking_time(self, values):
        """Функция проверки поля времени приготовления."""
        if values < MIN_TIME_COOKING:
            raise serializers.ValidationError(
                f'Время приготовление не может быть меньше {MIN_TIME_COOKING}'
            )
        return values

    def validate_name(self, values):
        """Функция провеки поля названия рецепта."""
        if not values:
            raise serializers.ValidationError(
                'Необходимо указать название рецепта!'
            )
        return values

    def validate_text(self, values):
        """Функция проверки описания рецепта."""
        if not values:
            raise serializers.ValidationError(
                'Необходимо написать описание рецепта!'
            )
        return values

    def create(self, validated_data):
        """Функция создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount'),
                measurement_unit=ingredient.get('measurement_unit'),
            )
        return recipe

    def update(self, instance, validated_data):
        """Функция обновления рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredientinrecipe.all().delete()
        for ingredient_data in ingredients:
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient_data.get('ingredient'),
                amount=ingredient_data.get('amount'),
                measurement_unit=ingredient_data.get('measurement_unit'),
            )
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data

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
