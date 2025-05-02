from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter

from backend.api.serializers.recipes import IngredientSerializer, TagSerializer
from backend.recipes.models import Ingredient, Tag


class ListRetrieveViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Класс для наследования. Возвращает список объектов или объект."""


class IngredientViewSet(ListRetrieveViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ListRetrieveViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей."""
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    pass