from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    RecipesInShoppingList,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тегов."""
    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""
    list_display = ('id', 'name', 'author', 'cooking_time')
    filter_horizontal = ('tags', 'ingredients')
    list_filter = ('tags',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Админка для ингредиентов в рецепте."""
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    list_select_related = ('ingredient', 'recipe')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe', 'ingredient')


@admin.register(RecipesInShoppingList)
class RecipesInShoppingListAdmin(admin.ModelAdmin):
    """Админка для рецептов в списке покупок."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для избранного."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user',)
