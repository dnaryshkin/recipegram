from rest_framework import serializers

from backend.api.serializers.recipe_serializers import MiniRecipeSerializer
from backend.recipes.models import Recipe
from backend.users.models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор получения подписки пользователя."""
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='following.avatar')

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """Функция проверки подписки на пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                following=obj.following,
            ).exists()
        return False

    def get_recipes(self, obj):
        """Функция получения рецептов."""
        recipes = Recipe.objects.filter(author=obj.following)
        request = self.context.get('request')
        if request:
            limit = request.query_params.get('recipes_limit')
            if limit:
                recipes = recipes[:int(limit)]
        return MiniRecipeSerializer(recipes,
                                    many=True,
                                    context=self.context
                                    ).data

    def get_recipes_count(self, obj):
        """Функция получения количества рецептов пользователя."""
        return Recipe.objects.filter(author=obj.following).count()


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки на пользователя."""

    class Meta:
        model = Subscription
        fields = (
            'id',
            'user',
            'following',
        )

    def validate(self, data):
        """Функция валидации подписки."""
        user = self.context.get('request').user
        following = data.get('following')
        if user == following:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        if Subscription.objects.filter(
                user=user,
                following=following,
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписались на данного пользователя!'
            )
        return data

    def create(self, validated_data):
        """Функция создания подписки на пользователя."""
        return Subscription.objects.create(**validated_data)

    def to_representation(self, instance):
        return SubscriptionSerializer(instance, context=self.context).data