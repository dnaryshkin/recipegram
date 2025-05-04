from django_filters import rest_framework as filters
import django_filters

from recipes.models import Ingredient


class IngredientFilter(filters.FilterSet):
    """Класс для фильтрации ингредиентов по названию."""
    name = django_filters.CharFilter(
        field_name='name',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Класс для фильтрации рецептов."""
    pass