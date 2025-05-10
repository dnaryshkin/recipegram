from django.db.models import Sum

from recipes.models import IngredientInRecipe


class CreateShoppingList(object):
    """Класс создания списка покупок."""

    @staticmethod
    def create_list(user):
        """Функция создания списка покупок."""
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__in_shopping_lists__user=user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit'
            )
            .annotate(total=Sum('amount'))
            .order_by('ingredient__name')
        )

        return [
            f"{ing['ingredient__name']} "
            f"({ing['ingredient__measurement_unit']}) — {ing['total']}"
            for ing in ingredients
        ]
