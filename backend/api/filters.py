from django_filters import rest_framework as filters
import django_filters
from django.db.models import Q
from recipes.models import Ingredient, Tag


class IngredientFilter(filters.FilterSet):
    """Класс для фильтрации ингредиентов по названию."""
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Класс для фильтрации рецептов по тегам, автору и избранному."""
    tags = filters.MultipleChoiceFilter(
        field_name='tags__slug',
        conjoined=False,
        method='filter_tags',
        choices=Tag.objects.values_list('slug', 'slug')
    )
    author = filters.NumberFilter(
        field_name='author__id',
        method='filter_author'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_tags(self, queryset, name, value):
        """Фильтрация рецептов по нескольким тегам."""
        if not value:
            return queryset
        if isinstance(value, str):
            value = value.split(',')
        tag_query = Q()
        for slug in value:
            tag_query |= Q(tags__slug=slug)
        return queryset.filter(tag_query).distinct()

    def filter_author(self, queryset, name, value):
        """Фильтрация рецептов по автору."""
        if not value:
            return queryset
        return queryset.filter(author__id=value)

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация рецептов добавленных в избранное."""
        if not value or not self.request.user.is_authenticated:
            return queryset
        return queryset.filter(favorite__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов добавленных в список покупок."""
        if not value or not self.request.user.is_authenticated:
            return queryset
        return queryset.filter(in_shopping_lists__user=self.request.user)