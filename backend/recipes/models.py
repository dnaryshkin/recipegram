from django.core.validators import MinValueValidator, MaxValueValidator, \
    RegexValidator
from django.db import models
from backend.foodgram_backend.constants import (
    MAX_NAME_TAG_LENGTH,
    MAX_SLUG_TAG_LENGTH,
    MAX_NAME_INGREDIENT_LENGTH,
    MAX_UNIT_LENGTH,
    MAX_NAME_RECIPE_LENGTH,
    MIN_TIME_COOKING,
    MIX_AMOUNT_INGREDIENTS,
)

from backend.users.models import User


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
        verbose_name='тег'
        verbose_name_plural='Теги'

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
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        max_length=MAX_NAME_RECIPE_LENGTH,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
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
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'рецепт'
        verbose_name_plural= 'Рецепты'

    def __str__(self):
        return f'Рецепт: {self.name}'


class IngredientInRecipe(Recipe):
    """Модель ингредиентов в рецепте."""
    name = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=''
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиентов',
        validators=[
            MinValueValidator(
                MIX_AMOUNT_INGREDIENTS,
                message='Количество ингредиентов не может быть '
                        f'меньше {MIX_AMOUNT_INGREDIENTS}',
            ),
        ],
    )

    class Meta:
        ordering = ('name', 'recipe',)
        verbose_name = 'ингедицент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (f'Ингредиент {self.name} в количестве {self.amount} '
                f'{self.name.measurement_unit}')




