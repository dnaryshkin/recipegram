from recipes.models import RecipesInShoppingList
from rest_framework import serializers

from api.serializers.recipes import MiniRecipeSerializer


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели добавления рецепта в список покупок."""

    class Meta:
        model = RecipesInShoppingList
        fields = ('user', 'recipe')

    def validate(self, data):
        """Функция проверки добавления в список покупок."""
        user = self.context['request'].user
        recipe = data['recipe']
        if RecipesInShoppingList.objects.filter(
                user=user,
                recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок!'
            )
        return data

    def to_representation(self, instance):
        return MiniRecipeSerializer(instance.recipe, context=self.context).data
