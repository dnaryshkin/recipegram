from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers.recipes import (
    IngredientSerializer,
    MiniRecipeSerializer,
    ReadRecipeSerializer,
    RecipeSerializer,
    TagSerializer,
)
from api.serializers.subscription import (
    CreateSubscriptionSerializer,
    SubscriptionSerializer,
)
from api.serializers.users import (
    AvatarSerializer,
    ChangePasswordSerializer,
    CreateUserSerializer,
    ReadUserSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    RecipesInShoppingList,
    Tag,
)
from users.models import Subscription, User


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
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = RecipeSerializer

    def get_permissions(self):
        """Функция выбора прав доступа."""
        if self.action in ('create', 'shopping_cart', 'favorite'):
            return (IsAuthenticated(),)
        if self.action in ('update', 'partial_update', 'destroy'):
            return (IsAuthorOrReadOnly(),)
        return (AllowAny(),)

    def get_serializer_class(self):
        """Функция выбора сериализатора."""
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeSerializer
        return super().get_serializer()

    def get_serializer(self, *args, **kwargs):
        if self.action in ('update', 'partial_update'):
            kwargs['partial'] = False
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        """Функция сохраняет рецепт устанавливая пользователя автором."""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=(AllowAny,),
    )
    def get_link(self, request, pk=None):
        """Функция получения короткой ссылки рецепта."""
        recipe = self.get_object()
        short_link = reverse(
            'short-link',
            kwargs={'pk': recipe.pk}
        )
        full_short_link = request.build_absolute_uri(short_link)
        return Response(
            {'short-link': full_short_link},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
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
            serializer = MiniRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        if request.method == 'DELETE':
            recipe_shop_list = RecipesInShoppingList.objects.filter(
                recipe=recipe,
                user=user,
            ).first()
            if recipe_shop_list:
                recipe_shop_list.delete()
                return Response(
                    'Рецепт удален из списка покупок!',
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    'Рецепт не добавлен в список покупок!',
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
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
        permission_classes=(IsAuthenticated,),
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
            serializer = MiniRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        if request.method == 'DELETE':
            recipe_favorite = Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).first()
            if recipe_favorite:
                recipe_favorite.delete()
                return Response(
                    'Данный рецепт удален из избранного!',
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    'Рецепта не было в избранном!',
                    status=status.HTTP_400_BAD_REQUEST,
                )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return ReadUserSerializer

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Функция добавления или удаления аватара текущего пользователя."""
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """Функция отображения профиля текущего пользователя."""
        serializer = ReadUserSerializer(request.user,
                                        context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """
        Функция отображения подписок пользователя на других пользователей.
        """
        subscriptions = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """Подписка или отписка от пользователя."""
        user = request.user
        following = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            serializer = CreateSubscriptionSerializer(
                data={'user': user.id, 'following': following.pk},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                following=following
            )
            if not subscription.exists():
                return Response(
                    'Вы не подписаны на этого пользователя.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        """Функция смены пароля пользователя."""
        password_serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if password_serializer.is_valid():
            current_user = request.user
            current_user.set_password(
                password_serializer.validated_data['new_password']
            )
            current_user.save()
            return Response(
                'Пароль изменен!',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(password_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeRedirectView(viewsets.ViewSet):
    """Перенаправление на полный рецепт по короткой ссылке."""

    def link_redirect(self, request, pk):
        """Функция перенаправления на страницу рецепта."""
        recipe = get_object_or_404(Recipe, pk=pk)
        full_recipe_url = request.build_absolute_uri(f'/recipes/{recipe.pk}/')
        return redirect(full_recipe_url)
