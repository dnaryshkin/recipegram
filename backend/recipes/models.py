from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from foodgram_backend.constants import (MAX_NAME_INGREDIENT_LENGTH,
                                        MAX_NAME_RECIPE_LENGTH,
                                        MAX_NAME_TAG_LENGTH,
                                        MAX_SLUG_TAG_LENGTH, MAX_UNIT_LENGTH,
                                        MIN_AMOUNT_INGREDIENTS,
                                        MIN_TIME_COOKING)
from users.models import User


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=MAX_NAME_TAG_LENGTH,
        unique=True,
        verbose_name='Название тега',
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_TAG_LENGTH,
        unique=True,
        verbose_name='Слаг тега',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9-_]+$',
                message='Тег может содержать только латинские буквы, '
                        'цифры или дефис!'
            )
        ],
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Тег: {self.name}'


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=MAX_NAME_INGREDIENT_LENGTH,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=MAX_UNIT_LENGTH,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'), name='unique_ingredient'
            ),
        )

    def __str__(self):
        return f'Ингредиент: {self.name}'


class Recipe(models.Model):
    """Модель рецепта."""
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        related_name='recipe_ingredients',
    )
    name = models.CharField(
        max_length=MAX_NAME_RECIPE_LENGTH,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение рецепта',
        help_text='Загрузите изображение блюда.',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text="Опишите рецепт."
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_TIME_COOKING,
                message='Время готовки не может быть меньше '
                        f'{MIN_TIME_COOKING}'
            ),
        ],
        help_text='Время приготовления указывается в минутах',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Рецепт: {self.name}'


class IngredientInRecipe(models.Model):
    """Модель связи ингредиентов в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient_amounts',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиентов',
        validators=[
            MinValueValidator(
                MIN_AMOUNT_INGREDIENTS,
                message='Количество ингредиентов не может быть '
                        f'меньше {MIN_AMOUNT_INGREDIENTS}',
            ),
        ],
    )

    class Meta:
        ordering = ('ingredient', 'recipe',)
        verbose_name = 'ингедицент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (
            f'Ингредиент {self.ingredient.name} в количестве {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class RecipesInShoppingList(models.Model):
    """Модель списка покупок рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_lists',
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'рецепты в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

    def __str__(self):
        return (
            f'Рецепт: {self.recipe.name} в списке покупок у '
            f'{self.user.username}'
        )


class Favorite(models.Model):
    """Модель добавления рецепта в избранное."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
