from django.db.models import Sum

from recipes.models import IngredientInRecipe, Recipe


class CreateShoppingList(object):
    """Класс создания списка покупок."""

    @staticmethod
    def create_list(user):
        """Функция создания списка покупок."""
        recipes = Recipe.objects.filter(in_shopping_lists__user=user)
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            total_amount=Sum('amount'),
        )
        shopping_list = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            ingredient_shopping = f'{name} ({unit}) — {amount}'
            shopping_list.append(ingredient_shopping)
        return shopping_list
