from django.db.models import Sum

from recipes.models import IngredientInRecipe


class CreateShoppingList(object):
    """Класс создания списка покупок."""

    @staticmethod
    def create_list(user):
        """Функция создания списка покупок."""
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in_shopping_lists__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            total_amount=Sum('amount'),
        )
        shopping_list = []
        for ingredient in ingredients:
            line = (
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) — "
                f"{ingredient['total_amount']}"
            )
            shopping_list.append(line)
        return shopping_list
