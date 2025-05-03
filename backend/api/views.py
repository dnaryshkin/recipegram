from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers.recipes import IngredientSerializer, \
    TagSerializer, ReadRecipeSerializer, RecipeSerializer, MiniRecipeSerializer
from recipes.models import Ingredient, Tag, Recipe, \
    RecipesInShoppingList, Favorite, IngredientInRecipe

User = get_user_model()


class ListRetrieveViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Класс для наследования. Возвращает список объектов или объект."""


class IngredientViewSet(ListRetrieveViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)


class TagViewSet(ListRetrieveViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAdminAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        """Функция выбора сериализатора."""
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """Функция сохраняет рецепт устанавливая пользователя автором."""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def get_link(self, request, pk=None):
        """Функция получения короткой ссылки рецепта."""
        recipe = self.get_object()
        short_link = reverse(
            'short-link',
            kwargs={'pk': recipe.pk}
        )
        full_short_link = request.build_absolute_uri(short_link)
        return Response({'short-link': full_short_link})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk=None):
        """Функция добавления/удаления рецепта в список покупок."""
        recipe = self.get_object()
        user = self.request.user
        if request.method == 'POST':
            if RecipesInShoppingList.objects.filter(
                    recipe=recipe,
                    user=user
            ).exists():
                return Response(
                    'Рецепт уже был добавлен в список покупок',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            RecipesInShoppingList.objects.create(
                recipe=recipe,
                user=user,
            )
            return Response(
                MiniRecipeSerializer.data,
                status=status.HTTP_201_CREATED,
            )
        if request.method == 'DELETE':
            recipe_shop_list = RecipesInShoppingList.objects.filter(
                recipe=recipe,
                user=user,
            ).first()
            if not recipe_shop_list:
                recipe_shop_list.delete()
                return Response(
                    'Рецепт удален из списка покупок!',
                    status=status.HTTP_204_NO_CONTENT,
                )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Функция скачивания списка покупок в формате txt."""
        user = self.request.user
        recipes_shop_list = Recipe.objects.filter(in_shopping_lists__user=user)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in=recipes_shop_list
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            total_amount=Sum('amount'),
        )
        list_shopping = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            ingredient_shopping = f'{name} ({unit}) — {amount}'
            list_shopping.append(ingredient_shopping)
        responce = HttpResponse(
            '\n'.join(list_shopping),
            content_type='text/plain',
        )
        responce['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return responce

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk=None):
        """Функция добавления/удаления рецепта в избранное."""
        recipe = self.get_object()
        user = self.request.user
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Данный рецепт уже находится в избранном!',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                MiniRecipeSerializer.data,
                status=status.HTTP_201_CREATED,
            )
        if request.method == 'DELETE':
            recipe_favorite = RecipesInShoppingList.objects.filter().first()
            if recipe_favorite:
                recipe_favorite.delete()
                return Response(
                    'Данный рецепт удален из избранного!',
                    status=status.HTTP_204_NO_CONTENT,
                )

# class UserViewSet(viewsets.ModelViewSet):
#     """Вьюсет для пользователей."""
#     queryset = User.objects.all()
#     pagination_class = CustomPageNumberPagination
#
#     def get_serializer_class(self):
#
#         if self.action == 'create':
#             return CreateUserSerializer
#         elif self.action == 'set_password':
#             return ChangePasswordSerializer
#         elif self.action == 'avatar':
#             return AvatarSerializer
#         return ReadUserSerializer
#
#
# @action(detail=True, methods=['post'])
#
#
# def set_password(self, request, pk=None):
#     user = self.get_object()
#     serializer = PasswordSerializer(data=request.data)
#     if serializer.is_valid():
#         user.set_password(serializer.validated_data['password'])
#         user.save()
#         return Response({'status': 'password set'})
#     else:
#         return Response(serializer.errors,
#                         status=status.HTTP_400_BAD_REQUEST)
#
#
# @action(detail=True, methods=["put"], name="Change Password")
# def password(self, request, pk=None):
#     """Update the user's password."""
#     ...
#
#
# @password.mapping.delete
# def delete_password(self, request, pk=None):
#     """Delete the user's password."""
#     ...
#
#
# class SubscriberViewSet(viewsets.ModelViewSet):
#     """Вьюсет для подписок."""
#     serializer_class = S
