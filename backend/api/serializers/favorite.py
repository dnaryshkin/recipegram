from rest_framework import serializers

from backend.api.serializers.recipes import MiniRecipeSerializer
from backend.recipes.models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Избранного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """Функция проверки добавления в избранное."""
        user = self.context['request'].user
        recipe = data['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное!'
            )
        return data

    def to_representation(self, instance):
        return MiniRecipeSerializer(instance.recipe, context=self.context).data