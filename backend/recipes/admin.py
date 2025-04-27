from django.contrib import admin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientInRecipe,
    RecipesInShoppingList,
    Favorite,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тегов."""
    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""
    pass


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Админка для ингредиентов в рецепте."""
    pass


@admin.register(RecipesInShoppingList)
class RecipesInShoppingListAdmin(admin.ModelAdmin):
     """Админка для рецептов в списке покупок."""
     pass


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для подписок."""
    pass