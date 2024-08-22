from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from .models import (
    Ingredient,
    Tag,
    Recipe,
    ShoppingCart,
    Favorite,
    IngredientInRecipe,
)

admin.site.empty_value_display = 'Здесь пока ничего нет:('


class IngredientInRecipeInline(admin.TabularInline):
    """Связанная админ панель для ингредиентов в рецепте."""

    model = IngredientInRecipe
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ панель для ингредиентов."""

    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ панель для тегов."""

    list_display = (
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )
    list_filter = (
        'name',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """"Админ панель для рецептов."""

    list_display = (
        'author',
        'name',
        'favorite_additions',
    )
    list_editable = (
        'name',
    )
    search_fields = (
        'author__username',
        'name',
    )
    list_filter = (
        'tags',
    )
    inlines = (IngredientInRecipeInline,)

    @admin.display(description='Добавлений в избранное')
    def favorite_additions(self, obj):
        """Считает кол-во добавлений рецепта в избранное."""

        return obj.favorites.all().count()

    def save_related(self, request, form, formsets, change):
        """Проверка перед сохранением рецепта."""

        super().save_related(request, form, formsets, change)
        if not form.instance.ingredients_in_recipe.exists():
            self.message_user(
                request,
                'Нельзя сохранить рецепт без ингредиентов.',
                level=messages.ERROR
            )
            form.instance.delete()
            return HttpResponseRedirect(request.path_info)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """"Админ панель для рецептов."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
    )
    list_filter = (
        'user',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ панель для избранного."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
    )
    list_filter = (
        'user',
    )
