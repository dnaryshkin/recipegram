from django.core.validators import MinValueValidator
from rest_framework import serializers

from api.serializers.base64 import Base64ImageField
from api.serializers.users import ReadUserSerializer
from foodgram_backend.constants import MIN_AMOUNT_INGREDIENTS, MIN_TIME_COOKING
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    RecipesInShoppingList,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ингредиент."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор связи для ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для указания количества ингредиента в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        required=True,
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT_INGREDIENTS),
        ],
        required=True,
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения (чтения) рецепта."""
    tags = TagSerializer(many=True, read_only=True)
    author = ReadUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredient_amounts',
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
        validated_data.pop('author', None)
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount'),
            )
        return recipe

    def update(self, instance, validated_data):
        """Функция обновления рецепта."""
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients is not None:
            instance.recipe_ingredient_amounts.all().delete()
            for ingredient_data in ingredients:
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data.get('ingredient'),
                    amount=ingredient_data.get('amount'),
                )
        return instance

    def to_representation(self, instance):
        """Функция предоставления информации в виде ReadRecipeSerializer."""
        return ReadRecipeSerializer(instance, context=self.context).data
